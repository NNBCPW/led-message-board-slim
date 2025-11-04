import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------
# INTERACTIVE LED MESSAGE BOARD — Compact, Full Keyboard
# ---------------------------------------------------
st.set_page_config(page_title="Interactive LED Board", layout="centered")

st.markdown("""
<style>
body { background-color: #141414; }
canvas {
  background-color: #141414;
  display: block;
  margin: auto;
  border-radius: 12px;
  box-shadow: inset 0 0 30px #000;
}
/* Hidden input to enable mobile keyboards */
#hidden-led-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  height: 0;
  width: 0;
}
</style>
""", unsafe_allow_html=True)

html_code = """
<input id="hidden-led-input" type="text" inputmode="text" autocomplete="off" autocorrect="off" autocapitalize="none" spellcheck="false" />
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

// ---------- DIMENSIONS ----------
function tW(){return DOT_W*DOT_SIZE+(DOT_W-1)*DOT_GAP+TILE_PAD*2;}
function tH(){return DOT_H*DOT_SIZE+(DOT_H-1)*DOT_GAP+TILE_PAD*2;}
const TW=tW(), TH=tH();
const BW=OUTER_PAD*2+COLS*TW+(COLS-1)*TILE_GAP;
const BH=OUTER_PAD*2+ROWS*TH+(ROWS-1)*TILE_GAP;

const c=document.getElementById("ledBoard");
const ctx=c.getContext("2d");
c.width=BW; 
c.height=BH;

// Compact visual size to match your flashing board
const TARGET_W = 640;
c.style.width = TARGET_W + "px";
c.style.height = (BH * TARGET_W / BW) + "px";

// Hidden input for mobile keyboards
const hiddenInput = document.getElementById("hidden-led-input");

// Board state
let chars=Array(ROWS).fill().map(()=>Array(COLS).fill(" "));
let active={r:-1,c:-1};

// Cache for dynamically generated 5x7 patterns
const patternCache = new Map();

// ----- Render a character into a 5x7 pattern dynamically -----
// This supports *all printable* characters by rasterizing a font and sampling into the 5x7 grid.
function patternForChar(ch) {
  if (patternCache.has(ch)) return patternCache.get(ch);

  // Render char to an offscreen canvas at higher res, then downsample
  const scale = 12; // pixels per dot
  const W = DOT_W * scale;
  const H = DOT_H * scale;
  const t = document.createElement("canvas");
  t.width = W; t.height = H;
  const tctx = t.getContext("2d");

  // Fill bg
  tctx.fillStyle = "black";
  tctx.fillRect(0,0,W,H);

  // Choose a font and size that fills the box nicely
  // We'll iterate a couple sizes to get good coverage without clipping.
  const candidates = [H*0.95, H*0.9, H*0.85];
  let metrics, usedSize = candidates[candidates.length-1];
  tctx.textAlign = "center";
  tctx.textBaseline = "middle";
  tctx.fillStyle = "white";
  for (let sz of candidates) {
    tctx.clearRect(0,0,W,H);
    tctx.fillRect(0,0,W,H); // bg black first
    tctx.globalCompositeOperation = "source-over";
    tctx.fillStyle = "white";
    tctx.font = `bold ${Math.floor(sz)}px monospace`;
    tctx.fillText(ch, W/2, H/2 + H*0.04); // slight vertical nudge
    // See how many white pixels we got
    const img = tctx.getImageData(0,0,W,H).data;
    let count = 0;
    for (let i=0; i<img.length; i+=4) if (img[i] > 127) count++;
    if (count > (W*H*0.05)) { usedSize = sz; break; } // enough pixels lit
  }

  // Draw final with chosen size
  tctx.clearRect(0,0,W,H);
  tctx.fillStyle = "black";
  tctx.fillRect(0,0,W,H);
  tctx.fillStyle = "white";
  tctx.font = `bold ${Math.floor(usedSize)}px monospace`;
  tctx.textAlign = "center";
  tctx.textBaseline = "middle";
  tctx.fillText(ch, W/2, H/2 + H*0.04);

  const img = tctx.getImageData(0,0,W,H).data;

  // Downsample to 5x7 by checking if any pixel in each cell is lit
  const pattern = [];
  for (let gy=0; gy<DOT_H; gy++) {
    let rowBits = "";
    for (let gx=0; gx<DOT_W; gx++) {
      let on = false;
      for (let py=gy*scale; py<(gy+1)*scale && !on; py++) {
        for (let px=gx*scale; px<(gx+1)*scale; px++) {
          const idx = (py*W + px) * 4;
          if (img[idx] > 127) { on = true; break; }
        }
      }
      rowBits += on ? "1" : "0";
    }
    pattern.push(rowBits);
  }

  patternCache.set(ch, pattern);
  return pattern;
}

// ----- Drawing helpers -----
function drawDot(x,y,on){
  ctx.beginPath();
  ctx.arc(x+DOT_SIZE/2,y+DOT_SIZE/2,DOT_SIZE/2,0,2*Math.PI);
  ctx.fillStyle=on?LED_ON:LED_OFF;
  ctx.fill();
}
function drawTile(ch,x,y){
  ctx.fillStyle=BG_COLOR;
  ctx.fillRect(x,y,TW,TH);
  ctx.strokeStyle=GAP_LINE;
  ctx.strokeRect(x,y,TW,TH);

  const p = (ch === " ")? Array(DOT_H).fill("00000") : patternForChar(ch);
  for(let gy=0;gy<DOT_H;gy++){
    for(let gx=0;gx<DOT_W;gx++){
      const on=p[gy][gx]==="1";
      const dx=x+TILE_PAD+gx*(DOT_SIZE+DOT_GAP);
      const dy=y+TILE_PAD+gy*(DOT_SIZE+DOT_GAP);
      drawDot(dx,dy,on);
    }
  }
}
function drawBoard(){
  ctx.fillStyle=BG_COLOR;
  ctx.fillRect(0,0,c.width,c.height);
  for(let r=0;r<ROWS;r++){
    for(let col=0;col<COLS;col++){
      const x=OUTER_PAD+col*(TW+TILE_GAP);
      const y=OUTER_PAD+r*(TH+TILE_GAP);
      drawTile(chars[r][col],x,y);
      if(active.r===r&&active.c===col){
        ctx.lineWidth=2;
        ctx.strokeStyle=LED_ON;
        ctx.strokeRect(x-1,y-1,TW+2,TH+2);
      }
    }
  }
}
drawBoard();

// ----- Selection helpers -----
function advanceCursor() {
  if (active.r < 0) return;
  if (active.c < COLS - 1) {
    active.c += 1;
  } else if (active.r < ROWS - 1) {
    active.r += 1;
    active.c = 0;
  } // else stick at last tile
}
function moveToPrev() {
  if (active.r < 0) return;
  if (active.c > 0) {
    active.c -= 1;
  } else if (active.r > 0) {
    active.r -= 1;
    active.c = COLS - 1;
  }
}

// ----- Click selection with scaling fix -----
c.addEventListener("click",e=>{
  const rect=c.getBoundingClientRect();
  const scaleX = c.width / rect.width;
  const scaleY = c.height / rect.height;
  const x=(e.clientX-rect.left)*scaleX - OUTER_PAD;
  const y=(e.clientY-rect.top )*scaleY - OUTER_PAD;
  const col=Math.floor(x/(TW+TILE_GAP));
  const r=Math.floor(y/(TH+TILE_GAP));
  if(r>=0&&r<ROWS&&col>=0&&col<COLS){
    active={r:r,c:col};
    drawBoard();
    // Focus hidden input so mobile shows a keyboard
    hiddenInput.value = "";
    hiddenInput.focus({preventScroll:true});
  }
});

// ----- Keyboard input handling -----
// Desktop: keydown; Mobile: use hidden input's input event
document.addEventListener("keydown", e => {
  // Ensure we only act when a tile is active
  if (active.r < 0) return;

  if (e.key === "Backspace") {
    e.preventDefault();
    chars[active.r][active.c] = " ";
    drawBoard();
    return;
  }
  if (e.key === " " || e.code === "Space") {
    e.preventDefault();
    chars[active.r][active.c] = " ";
    advanceCursor();
    drawBoard();
    return;
  }

  // Printable single characters (letters, numbers, punctuation, symbols)
  if (e.key && e.key.length === 1) {
    const ch = e.key; // keep exact character (case + symbol)
    chars[active.r][active.c] = ch;
    advanceCursor();
    drawBoard();
  }
});

// Mobile text entry via hidden input (captures all printable chars)
hiddenInput.addEventListener("input", e => {
  if (active.r < 0) return;
  const v = hiddenInput.value;
  if (!v) return;
  const ch = v.slice(-1); // use last typed char
  // treat space specially per your rule
  if (ch === " ") {
    chars[active.r][active.c] = " ";
    advanceCursor();
    drawBoard();
  } else if (ch.length === 1) {
    chars[active.r][active.c] = ch;
    advanceCursor();
    drawBoard();
  }
  // keep input small
  hiddenInput.value = "";
});

// Optional: tap anywhere outside to blur the hidden input
document.addEventListener("click", e => {
  if (e.target !== c && e.target !== hiddenInput) {
    // do nothing; keeping focus helps mobile input flow
  }
});
</script>
"""

# compact render height proportional to 640px width
components.html(html_code, height=360)
