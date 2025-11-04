import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Interactive LED Board", layout="centered")

st.markdown("""
<style>
body {background-color: #111;}
canvas {
  background-color: #111;
  display: block;
  margin: 0 auto;
  border-radius: 12px;
  box-shadow: 0 0 30px #000 inset;
}
</style>
""", unsafe_allow_html=True)

html_code = """
<canvas id="ledBoard" width="1250" height="480"></canvas>
<script>
const canvas = document.getElementById('ledBoard');
const ctx = canvas.getContext('2d');

// Board config
const rowsPerBlock = 7;
const colsPerBlock = 5;
const totalRows = 6;
const totalCols = 12;
const dot = 8;
const spacing = 3;
const blockSpacing = 10;
const blockW = colsPerBlock * (dot + spacing);
const blockH = rowsPerBlock * (dot + spacing);
const onColor = "#FFD940";
const offColor = "#2f2f2f";
const borderColor = "#0a0a0a";

let boardChars = Array(totalRows).fill(0).map(() => Array(totalCols).fill(" "));
let activeRow = -1;
let activeCol = -1;

// --- LED FONT SET ---
// (Extended: letters, numbers, punctuation, arrows)
const FONT = {
  "A":["01110","10001","10001","11111","10001","10001","10001"],
  "B":["11110","10001","11110","10001","10001","10001","11110"],
  "C":["01110","10001","10000","10000","10000","10001","01110"],
  "D":["11110","10001","10001","10001","10001","10001","11110"],
  "E":["11111","10000","11100","10000","10000","10000","11111"],
  "F":["11111","10000","11100","10000","10000","10000","10000"],
  "G":["01110","10001","10000","10111","10001","10001","01111"],
  "H":["10001","10001","11111","10001","10001","10001","10001"],
  "I":["11111","00100","00100","00100","00100","00100","11111"],
  "J":["00111","00001","00001","00001","10001","10001","01110"],
  "K":["10001","10010","11100","10100","10010","10001","10001"],
  "L":["10000","10000","10000","10000","10000","10000","11111"],
  "M":["10001","11011","10101","10101","10001","10001","10001"],
  "N":["10001","11001","10101","10011","10001","10001","10001"],
  "O":["01110","10001","10001","10001","10001","10001","01110"],
  "P":["11110","10001","10001","11110","10000","10000","10000"],
  "Q":["01110","10001","10001","10001","10101","10010","01101"],
  "R":["11110","10001","10001","11110","10100","10010","10001"],
  "S":["01111","10000","10000","01110","00001","00001","11110"],
  "T":["11111","00100","00100","00100","00100","00100","00100"],
  "U":["10001","10001","10001","10001","10001","10001","01110"],
  "V":["10001","10001","10001","10001","01010","01010","00100"],
  "W":["10001","10001","10101","10101","10101","11011","10001"],
  "X":["10001","01010","00100","00100","01010","10001","10001"],
  "Y":["10001","01010","00100","00100","00100","00100","00100"],
  "Z":["11111","00010","00100","01000","10000","10000","11111"],
  "0":["01110","10001","10011","10101","11001","10001","01110"],
  "1":["00100","01100","00100","00100","00100","00100","01110"],
  "2":["01110","10001","00001","00010","00100","01000","11111"],
  "3":["11110","00001","00001","01110","00001","00001","11110"],
  "4":["10010","10010","10010","11111","00010","00010","00010"],
  "5":["11111","10000","11110","00001","00001","10001","01110"],
  "6":["01110","10001","10000","11110","10001","10001","01110"],
  "7":["11111","00001","00010","00100","01000","01000","01000"],
  "8":["01110","10001","10001","01110","10001","10001","01110"],
  "9":["01110","10001","10001","01111","00001","10001","01110"],
  "-":["00000","00000","00000","11111","00000","00000","00000"],
  ".":["00000","00000","00000","00000","00000","01100","01100"],
  "!":["00100","00100","00100","00100","00000","00100","00100"],
  "?":["01110","10001","00010","00100","00100","00000","00100"],
  ">":["10000","01000","00100","00010","00100","01000","10000"],
  "<":["00001","00010","00100","01000","00100","00010","00001"],
  ":":["00000","01100","01100","00000","01100","01100","00000"],
  " ":["00000","00000","00000","00000","00000","00000","00000"]
};

// draw single LED letter
function drawLetter(char, xOffset, yOffset) {
  const pattern = FONT[char] || FONT[" "];
  for (let r = 0; r < rowsPerBlock; r++) {
    for (let c = 0; c < colsPerBlock; c++) {
      const x = xOffset + c * (dot + spacing);
      const y = yOffset + r * (dot + spacing);
      const color = pattern[r][c] === "1" ? onColor : offColor;
      ctx.beginPath();
      ctx.arc(x + dot/2, y + dot/2, dot/2, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
    }
  }
  ctx.strokeStyle = borderColor;
  ctx.lineWidth = 1.3;
  ctx.strokeRect(xOffset - spacing/2, yOffset - spacing/2, blockW + spacing, blockH + spacing);
}

// draw full board
function drawBoard() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (let row = 0; row < totalRows; row++) {
    for (let col = 0; col < totalCols; col++) {
      const xOffset = col * (blockW + blockSpacing);
      const yOffset = row * (blockH + blockSpacing);
      drawLetter(boardChars[row][col], xOffset, yOffset);
      if (row === activeRow && col === activeCol) {
        ctx.strokeStyle = "#FFD940";
        ctx.lineWidth = 2;
        ctx.strokeRect(xOffset - spacing/2, yOffset - spacing/2, blockW + spacing, blockH + spacing);
      }
    }
  }
}
drawBoard();

// click detection
canvas.addEventListener("click", e => {
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const col = Math.floor(x / (blockW + blockSpacing));
  const row = Math.floor(y / (blockH + blockSpacing));
  activeRow = row;
  activeCol = col;
  drawBoard();
});

// key typing
document.addEventListener("keydown", e => {
  if (activeRow >= 0 && activeCol >= 0) {
    let key = e.key;
    if (key.length === 1) {
      boardChars[activeRow][activeCol] = key.toUpperCase();
      drawBoard();
    } else if (key === "Backspace") {
      boardChars[activeRow][activeCol] = " ";
      drawBoard();
    } else if (key === "ArrowRight") {
      activeCol = Math.min(totalCols - 1, activeCol + 1);
      drawBoard();
    } else if (key === "ArrowLeft") {
      activeCol = Math.max(0, activeCol - 1);
      drawBoard();
    } else if (key === "ArrowDown") {
      activeRow = Math.min(totalRows - 1, activeRow + 1);
      drawBoard();
    } else if (key === "ArrowUp") {
      activeRow = Math.max(0, activeRow - 1);
      drawBoard();
    }
  }
});
</script>
"""
components.html(html_code, height=520)
