import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Interactive LED Message Board", layout="centered")

st.markdown(
    """
    <style>
    body {background-color: #111;}
    canvas {
        background-color: #111;
        display: block;
        margin: 0 auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

html_code = """
<canvas id="ledBoard" width="900" height="140"></canvas>
<script>
const canvas = document.getElementById('ledBoard');
const ctx = canvas.getContext('2d');
const rows = 7, cols = 5, blocks = 10;
const dot = 15, spacing = 5;
const blockW = cols * (dot + spacing);
const blockH = rows * (dot + spacing);
const onColor = "#FFD940";
const offColor = "#303030";

let characters = Array(blocks).fill(" ");
let activeBlock = -1;

function drawLED(char, xOffset) {
  const temp = document.createElement("canvas");
  temp.width = cols * 10;
  temp.height = rows * 10;
  const tctx = temp.getContext("2d");
  tctx.fillStyle = "white";
  tctx.font = "bold 50px monospace";
  tctx.fillText(char, 5, 40);
  const img = tctx.getImageData(0, 0, temp.width, temp.height);

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      let on = false;
      for (let pr = 0; pr < 10; pr++) {
        for (let pc = 0; pc < 10; pc++) {
          let idx = ((r*10+pr)*temp.width + (c*10+pc))*4;
          if (img.data[idx] > 128) on = true;
        }
      }
      ctx.beginPath();
      ctx.arc(
        xOffset + c*(dot+spacing) + dot/2,
        r*(dot+spacing) + dot/2,
        dot/2, 0, 2*Math.PI
      );
      ctx.fillStyle = on ? onColor : offColor;
      ctx.fill();
    }
  }
}

function drawBoard() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (let i = 0; i < blocks; i++) {
    const x = i * (blockW + spacing*2);
    drawLED(characters[i], x);
    if (i === activeBlock) {
      ctx.strokeStyle = "#FFD940";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, 0, blockW, blockH);
    }
  }
}
drawBoard();

canvas.addEventListener("click", e => {
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  activeBlock = Math.floor(x / (blockW + spacing*2));
  drawBoard();
});

document.addEventListener("keydown", e => {
  if (activeBlock >= 0) {
    let key = e.key;
    if (key.length === 1) {
      characters[activeBlock] = key.toUpperCase();
      drawBoard();
    }
    if (key === "Backspace") {
      characters[activeBlock] = " ";
      drawBoard();
    }
  }
});
</script>
"""
components.html(html_code, height=200)
