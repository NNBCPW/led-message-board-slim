import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Interactive LED Board", layout="centered")

st.markdown("""
<style>
body { background-color:#141414; }
canvas{
  background-color:#141414;
  display:block; margin:auto;
  border-radius:12px;
  box-shadow:inset 0 0 30px #000;
}
</style>
""", unsafe_allow_html=True)

html_code = r"""
<canvas id="ledBoard"></canvas>
<script>
// ---------- COLORS ----------
const LED_ON   = "#F9ED32";
const LED_OFF  = "#3B3C3D";
const BG_COLOR = "#141414";
const GAP_LINE = "#222222";

// ---------- GRID ----------
const ROWS=4, COLS=10;
const DOT_W=5, DOT_H=7;
const DOT_SIZE=10, DOT_GAP=4;
const TILE_PAD=6, TILE_GAP=6, OUTER_PAD=10;

// ---------- GEOMETRY HELPERS ----------
function tileW(){ return DOT_W*DOT_SIZE + (DOT_W-1)*DOT_GAP + 2*TILE_PAD; }
function tileH(){ return DOT_H*DOT_SIZE + (DOT_H-1)*DOT_GAP + 2*TILE_PAD; }
const TW = tileW(), TH = tileH();
const BOARD_W = OUTER_PAD*2 + COLS*TW + (COLS-1)*TILE_GAP;
const BOARD_H = OUTER_PAD*2 + ROWS*TH + (ROWS-1)*TILE_GAP;

// ---------- CANVAS + HiDPI ----------
const c = document.getElementById("ledBoard");
const ctx = c.getContext("2d", { alpha:false });
const dpr = window.devicePixelRatio || 1;
c.width  = Math.round(BOARD_W * dpr);
c.height = Math.round(BOARD_H * dpr);
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
const cssW = 640;
c.style.width  = cssW + "px";
c.style.height = (BOARD_H * cssW / BOARD_W) + "px";

// ---------- 5×7 FONT ----------
const FONT = { ... };  // (same font dictionary you already have)

// ---------- STATE ----------
let chars = Array.from({length:ROWS}, ()=>Array(COLS).fill(" "));
let active = { r:0, c:0 };

// ---------- DRAWING ----------
function drawDot(x,y,on){
  ctx.beginPath();
  ctx.arc(x+DOT_SIZE/2, y+DOT_SIZE/2, DOT_SIZE/2, 0, 2*Math.PI);
  ctx.fillStyle = on ? LED_ON : LED_OFF;
  ctx.fill();
}
function drawTile(ch, x, y){
  ctx.fillStyle = BG_COLOR;
  ctx.fillRect(x, y, TW, TH);
  ctx.strokeStyle = GAP_LINE;
  ctx.strokeRect(x, y, TW, TH);
  const p = FONT[ch] || FONT[" "];
  const sx = x + TILE_PAD, sy = y + TILE_PAD;
  for(let gy=0; gy<DOT_H; gy++){
    for(let gx=0; gx<DOT_W; gx++){
      const on = p[gy][gx] === "1";
      drawDot(sx + gx*(DOT_SIZE+DOT_GAP), sy + gy*(DOT_SIZE+DOT_GAP), on);
    }
  }
}
function drawBoard(){
  ctx.fillStyle = BG_COLOR;
  ctx.fillRect(0, 0, BOARD_W, BOARD_H);
  for(let r=0; r<ROWS; r++){
    for(let cidx=0; cidx<COLS; cidx++){
      const x = OUTER_PAD + cidx*(TW+TILE_GAP);
      const y = OUTER_PAD + r*(TH+TILE_GAP);
      drawTile(chars[r][cidx], x, y);
      if(active.r === r && active.c === cidx){
        ctx.lineWidth = 2;
        ctx.strokeStyle = LED_ON;
        ctx.strokeRect(x-1, y-1, TW+2, TH+2);
      }
    }
  }
}
drawBoard();

// ---------- MOBILE FOCUS + CLICK ----------
const hiddenInput = document.createElement("input");
hiddenInput.type = "text";
hiddenInput.style.position = "absolute";
hiddenInput.style.opacity = 0;
hiddenInput.style.height = 0;
hiddenInput.style.width = 0;
hiddenInput.style.zIndex = -1;
document.body.appendChild(hiddenInput);

c.addEventListener("click", (e)=>{
  const rect = c.getBoundingClientRect();
  const mx = (e.clientX - rect.left) * (c.width / rect.width) / (window.devicePixelRatio||1);
  const my = (e.clientY - rect.top)  * (c.height/ rect.height)/ (window.devicePixelRatio||1);
  const x = mx - OUTER_PAD, y = my - OUTER_PAD;
  const col = Math.floor(x / (TW + TILE_GAP));
  const row = Math.floor(y / (TH + TILE_GAP));
  if(row>=0 && row<ROWS && col>=0 && col<COLS){
    active = { r:row, c:col };
    drawBoard();
    hiddenInput.focus(); // mobile keyboard trigger
  }
});

// ---------- CURSOR MOVES ----------
function advance(){
  active.c += 1;
  if(active.c >= COLS){ active.c = 0; active.r = Math.min(active.r + 1, ROWS - 1); }
  drawBoard();
}
function backspace(){
  if(active.c > 0){ active.c -= 1; }
  else if(active.r > 0){ active.r -= 1; active.c = COLS - 1; }
  chars[active.r][active.c] = " ";
  drawBoard();
}

// ---------- TYPING ----------
document.addEventListener("keydown", (e)=>{
  if(active.r < 0) return;

  if(e.key === "Backspace"){ e.preventDefault(); backspace(); return; }
  if(e.key === "Enter"){ active.c = 0; active.r = Math.min(active.r+1, ROWS-1); drawBoard(); return; }
  if(e.key === " "){ e.preventDefault(); advance(); return; }

  if(e.key.length === 1){
    let ch = e.key;
    if(/[a-z]/.test(ch)) ch = ch.toUpperCase();
    if (FONT[ch]){ chars[active.r][active.c] = ch; advance(); }
  }
});
</script>
"""

components.html(html_code, height=440)
