import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Interactive LED Board", layout="centered")

st.markdown("""
<style>
body { background-color:#141414; }
canvas{
  background-color:#141414;
  display:block; 
  margin:auto;
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

// ---------- Responsive Scaling ----------
let cssW = 640; // desktop default
if (window.innerWidth < 768) { // mobile
  cssW = Math.min(window.innerWidth * 0.95, 640);
}
c.style.width  = cssW + "px";
c.style.height = (BOARD_H * cssW / BOARD_W) + "px";

// ---------- 5×7 FONT ----------
const FONT = {
" ":["00000","00000","00000","00000","00000","00000","00000"],
"A":["01110","10001","11111","10001","10001","10001","10001"],
"B":["11110","10001","11110","10001","10001","10001","11110"],
"C":["01110","10001","10000","10000","10000","10001","01110"],
"D":["11110","10001","10001","10001","10001","10001","11110"],
"E":["11111","10000","11110","10000","10000","10000","11111"],
"F":["11111","10000","11110","10000","10000","10000","10000"],
"G":["01110","10001","10000","10111","10001","10001","01110"],
"H":["10001","10001","11111","10001","10001","10001","10001"],
"I":["01110","00100","00100","00100","00100","00100","01110"],
"J":["00001","00001","00001","10001","10001","10001","01110"],
"K":["10001","10010","11100","10100","10010","10001","10001"],
"L":["10000","10000","10000","10000","10000","10000","11111"],
"M":["10001","11011","10101","10101","10001","10001","10001"],
"N":["10001","11001","10101","10011","10001","10001","10001"],
"O":["01110","10001","10001","10001","10001","10001","01110"],
"P":["11110","10001","11110","10000","10000","10000","10000"],
"Q":["01110","10001","10001","10001","10101","10010","01101"],
"R":["11110","10001","11110","10100","10010","10001","10001"],
"S":["01111","10000","10000","01110","00001","00001","11110"],
"T":["11111","00100","00100","00100","00100","00100","00100"],
"U":["10001","10001","10001","10001","10001","10001","01110"],
"V":["10001","10001","10001","01010","01010","00100","00100"],
"W":["10001","10001","10101","10101","10101","11011","10001"],
"X":["10001","01010","00100","00100","00100","01010","10001"],
"Y":["10001","01010","00100","00100","00100","00100","00100"],
"Z":["11111","00001","00010","00100","01000","10000","11111"],
"-":["00000","00000","00000","11111","00000","00000","00000"],
"!":["00100","00100","00100","00100","00100","00000","00100"],
"0":["01110","10001","10011","10101","11001","10001","01110"],
"1":["00100","01100","00100","00100","00100","00100","01110"],
"2":["01110","10001","00001","00110","01000","10000","11111"],
"3":["11110","00001","01110","00001","00001","00001","11110"],
"4":["00010","00110","01010","10010","11111","00010","00010"],
"5":["11111","10000","11110","00001","00001","10001","01110"],
"6":["01110","10000","11110","10001","10001","10001","01110"],
"7":["11111","00001","00010","00100","01000","01000","01000"],
"8":["01110","10001","01110","10001","10001","10001","01110"],
"9":["01110","10001","10001","01111","00001","00001","01110"],
".":["00000","00000","00000","00000","00000","00000","00100"]
};

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

// ---------- MOBILE KEYBOARD HANDLER ----------
const hiddenInput = document.createElement("input");
hiddenInput.type = "text";
hiddenInput.style.position = "fixed";
hiddenInput.style.opacity = 0;
hiddenInput.style.bottom = "0px";
hiddenInput.style.height = "1px";
hiddenInput.style.width = "1px";
hiddenInput.style.zIndex = 100;
document.body.appendChild(hiddenInput);

function focusInput() { hiddenInput.focus(); }

// ---------- CLICK / TOUCH ----------
c.addEventListener("click", handleInputFocus);
c.addEventListener("touchstart", handleInputFocus, {passive:true});
function handleInputFocus(e){
  const rect = c.getBoundingClientRect();
  const mx = (e.clientX - rect.left) * (c.width / rect.width) / (window.devicePixelRatio||1);
  const my = (e.clientY - rect.top)  * (c.height/ rect.height)/ (window.devicePixelRatio||1);
  const x = mx - OUTER_PAD, y = my - OUTER_PAD;
  const col = Math.floor(x / (TW + TILE_GAP));
  const row = Math.floor(y / (TH + TILE_GAP));
  if(row>=0 && row<ROWS && col>=0 && col<COLS){
    active = { r:row, c:col };
    drawBoard();
    focusInput(); // open keyboard
  }
}

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
