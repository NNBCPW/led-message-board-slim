import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------
# INTERACTIVE LED MESSAGE BOARD  (Matches Flashing Layout)
# ---------------------------------------------------
st.set_page_config(page_title="Interactive LED Board", layout="centered")

st.markdown("""
<style>
body {
  background-color: #141414;
}
canvas {
  background-color: #141414;
  display: block;
  margin: 0 auto;
  border-radius: 12px;
  box-shadow: inset 0 0 40px #000;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HTML + JS
# ---------------------------------------------------
html_code = """
<canvas id="ledBoard"></canvas>
<script>
// ---------- COLORS ----------
const LED_ON      = "#F9ED32";   // yellow
const LED_OFF     = "#3B3C3D";   // dark gray
const BG_COLOR    = "#141414";   // background
const GAP_LINE    = "#222222";   // faint gray

// ---------- GRID / TILE GEOMETRY ----------
const ROWS = 4, COLS = 10;
const DOT_W = 5, DOT_H = 7;
const DOT_SIZE  = 10;
const DOT_GAP   = 4;
const TILE_PAD  = 6;
const TILE_GAP  = 6;
const OUTER_PAD = 10;

// ---------- DERIVED SIZES ----------
function tileInnerW(){ return DOT_W * DOT_SIZE + (DOT_W - 1) * DOT_GAP; }
function tileInnerH(){ return DOT_H * DOT_SIZE + (DOT_H - 1) * DOT_GAP; }
function tileW(){ return tileInnerW() + TILE_PAD * 2; }
function tileH(){ return tileInnerH() + TILE_PAD * 2; }

const TILE_WIDTH  = tileW();
const TILE_HEIGHT = tileH();

const BOARD_WIDTH  = OUTER_PAD * 2 + COLS * TILE_WIDTH  + (COLS - 1) * TILE_GAP;
const BOARD_HEIGHT = OUTER_PAD * 2 + ROWS * TILE_HEIGHT + (ROWS - 1) * TILE_GAP;

const canvas = document.getElementById("ledBoard");
const ctx = canvas.getContext("2d");

// Perfect fit to match flashing board
canvas.width  = BOARD_WIDTH + 8;
canvas.height = BOARD_HEIGHT + 8;
canvas.style.width  = (BOARD_WIDTH + 8) + "px";
canvas.style.height = (BOARD_HEIGHT + 8) + "px";

// ---------- 5x7 FONT ----------
const FONT = {
 " ": ["00000","00000","00000","00000","00000","00000","00000"],
 "A": ["01110","10001","11111","10001","10001","10001","10001"],
 "B": ["11110","10001","11110","10001","10001","10001","11110"],
 "C": ["01110","10001","10000","10000","10000","10001","01110"],
 "D": ["11110","10001","10001","10001","10001","10001","11110"],
 "E": ["11111","10000","11110","10000","10000","10000","11111"],
 "F": ["11111","10000","11110","10000","10000","10000","10000"],
 "G": ["01110","10001","10000","10111","10001","10001","01110"],
 "H": ["10001","10001","11111","10001","10001","10001","10001"],
 "I": ["01110","00100","00100","00100","00100","00100","01110"],
 "J": ["00001","00001","00001","10001","10001","10001","01110"],
 "K": ["10001","10010","11100","10100","10010","10001","10001"],
 "L": ["10000","10000","10000","10000","10000","10000","11111"],
 "M": ["10001","11011","10101","10101","10001","10001","10001"],
 "N": ["10001","11001","10101","10011","10001","10001","10001"],
 "O": ["01110","10001","10001","10001","10001","10001","01110"],
 "P": ["11110","10001","11110","10000","10000","10000","10000"],
 "Q": ["01110","10001","10001","10001","10101","10010","01101"],
 "R": ["11110","10001","11110","10100","10010","10001","10001"],
 "S": ["01111","10000","10000","01110","00001","00001","11110"],
 "T": ["11111","00100","00100","00100","00100","00100","00100"],
 "U": ["10001","10001","10001","10001","10001","10001","01110"],
 "V": ["10001","10001","10001","01010","01010","00100","00100"],
 "W": ["10001","10001","10101","10101","10101","11011","10001"],
 "X": ["10001","01010","00100","00100","00100","01010","10001"],
 "Y": ["10001","01010","00100","00100","00100","00100","00100"],
 "Z": ["11111","00001","00010","00100","01000","10000","11111"],
 "-": ["00000","00000","00000","11111","00000","00000","00000"],
 "0": ["01110","10001","10011","10101","11001","10001","01110"],
 "1": ["00100","01100","00100","00100","00100","00100","01110"],
 "2": ["01110","10001","00001","00110","01000","10000","11111"],
 "3": ["01110","10001","00001","00110","00001","10001","01110"],
 "4": ["10010","10010","10010","11111","00010","00010","00010"],
 "5": ["11111","10000","11110","00001","00001","10001","01110"],
 "6": ["01110","10000","11110","10001","10001","10001","01110"],
 "7": ["11111","00001","00010","00100","01000","01000","01000"],
 "8": ["01110","10001","01110","10001","10001","10001","01110"],
 "9": ["01110","10001","10001","01111","00001","00001","01110"]
};

let chars = Array(ROWS).fill(0).map(()=>Array(COLS).fill(" "));
let active = {r:-1,c:-1};

// ---------- DRAW ----------
function drawDot(x, y, on) {
  ctx.beginPath();
  ctx.arc(x + DOT_SIZE/2, y + DOT_SIZE/2, DOT_SIZE/2, 0, 2*Math.PI);
  ctx.fillStyle = on ? LED_ON : LED_OFF;
  ctx.fill();
}

function drawTile(ch, x, y) {
  ctx.fillStyle = BG_COLOR;
  ctx.fillRect(x, y, TILE_WIDTH, TILE_HEIGHT);
  ctx.strokeStyle = GAP_LINE;
  ctx.strokeRect(x, y, TILE_WIDTH, TILE_HEIGHT);

  const pattern = FONT[ch] || FONT[" "];
  for (let gy = 0; gy < DOT_H; gy++) {
    for (let gx = 0; gx < DOT_W; gx++) {
      const on = pattern[gy][gx] === "1";
      const dx = x + TILE_PAD + gx * (DOT_SIZE + DOT_GAP);
      const dy = y + TILE_PAD + gy * (DOT_SIZE + DOT_GAP);
      drawDot(dx, dy, on);
    }
  }
}

function drawBoard() {
  ctx.fillStyle = BG_COLOR;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const x = OUTER_PAD + c * (TILE_WIDTH + TILE_GAP);
      const y = OUTER_PAD + r * (TILE_HEIGHT + TILE_GAP);
      drawTile(chars[r][c], x, y);
      if (active.r === r && active.c === c) {
        ctx.lineWidth = 2;
        ctx.strokeStyle = LED_ON;
        ctx.strokeRect(x - 1, y - 1, TILE_WIDTH + 2, TILE_HEIGHT + 2);
      }
    }
  }
}
drawBoard();

// ---------- CLICK TO SELECT ----------
canvas.addEventListener("click", (e)=>{
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left - OUTER_PAD;
  const y = e.clientY - rect.top - OUTER_PAD;
  const c = Math.floor(x / (TILE_WIDTH + TILE_GAP));
  const r = Math.floor(y / (TILE_HEIGHT + TILE_GAP));
  if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
    active = {r, c};
    drawBoard();
  }
});

// ---------- TYPE TO LIGHT TILE ----------
document.addEventListener("keydown", (e)=>{
  if (active.r >= 0 && active.c >= 0) {
    const key = e.key;
    if (key === "Backspace") {
      chars[active.r][active.c] = " ";
      drawBoard();
      return;
    }
    if (key.length === 1) {
      const upper = key.toUpperCase();
      if (FONT[upper]) {
        chars[active.r][active.c] = upper;
        active.c = Math.min(active.c + 1, COLS - 1);
        drawBoard();
      }
    }
  }
});
</script>
"""

# fixed canvas height that matches your flashing board geometry
components.html(html_code, height=462)
