import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="LED Message Board", layout="centered")

# --- global CSS ---
st.markdown("""
<style>
body {
  background-color: #0d0d0d;
}
canvas {
  background-color: #111;
  display: block;
  margin: 0 auto;
  border-radius: 20px;
  box-shadow: inset 0 0 40px #000;
}
</style>
""", unsafe_allow_html=True)

html_code = """
<canvas id="ledBoard" width="1360" height="540"></canvas>
<script>
const canvas = document.getElementById('ledBoard');
const ctx = canvas.getContext('2d');

// panel + LED sizing tuned to match reference layout
const rowsPerBlock = 7;
const colsPerBlock = 5;
const totalRows = 6;
const totalCols = 10;
const dot = 9;             // LED size
const spacing = 4;         // space between LEDs
const blockSpacing = 16;   // space between panels
const blockW = colsPerBlock * (dot + spacing);
const blockH = rowsPerBlock * (dot + spacing);

const onColor = "#FFD940";
const offColor = "#262626";
const panelColor = "#141414";
const borderColor = "#0b0b0b";

let boardChars = Array(totalRows).fill(0).map(()=>Array(totalCols).fill(" "));
let activeRow=-1, activeCol=-1;

// basic 7x5 font (extendable)
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
 "L":["10000","10000","10000","10000","10000","10000","11111"],
 "O":["01110","10001","10001","10001","10001","10001","01110"],
 "P":["11110","10001","10001","11110","10000","10000","10000"],
 "R":["11110","10001","10001","11110","10010","10001","10001"],
 "S":["01111","10000","10000","01110","00001","00001","11110"],
 "T":["11111","00100","00100","00100","00100","00100","00100"],
 "U":["10001","10001","10001","10001","10001","10001","01110"],
 "Y":["10001","01010","00100","00100","00100","00100","00100"],
 "-":["00000","00000","00000","11111","00000","00000","00000"],
 "0":["01110","10001","10011","10101","11001","10001","01110"],
 "1":["00100","01100","00100","00100","00100","00100","01110"],
 "2":["01110","10001","00001","00110","01000","10000","11111"],
 "3":["01110","10001","00001","00110","00001","10001","01110"],
 "4":["10010","10010","10010","11111","00010","00010","00010"],
 "5":["11111","10000","11110","00001","00001","10001","01110"],
 "6":["01110","10001","10000","11110","10001","10001","01110"],
 "7":["11111","00001","00010","00100","01000","01000","01000"],
 "8":["01110","10001","10001","01110","10001","10001","01110"],
 "9":["01110","10001","10001","01111","00001","00001","01110"],
 " ":["00000","00000","00000","00000","00000","00000","00000"]
};

function drawLED(x,y,on){
 ctx.beginPath();
 ctx.arc(x + dot/2, y + dot/2, dot/2, 0, 2*Math.PI);
 ctx.fillStyle = on ? onColor : offColor;
 ctx.fill();
}

function drawPanel(char,xOffset,yOffset){
 // panel background
 ctx.fillStyle = panelColor;
 ctx.fillRect(xOffset-4,yOffset-4,blockW+8,blockH+8);
 const pattern = FONT[char] || FONT[" "];
 for(let r=0;r<rowsPerBlock;r++){
   for(let c=0;c<colsPerBlock;c++){
     const px=xOffset + c*(dot+spacing);
     const py=yOffset + r*(dot+spacing);
     drawLED(px,py,pattern[r][c]==="1");
   }
 }
 ctx.strokeStyle = borderColor;
 ctx.lineWidth = 1.3;
 ctx.strokeRect(xOffset-4,yOffset-4,blockW+8,blockH+8);
}

function drawBoard(){
 ctx.clearRect(0,0,canvas.width,canvas.height);
 let startX=40;
 let startY=40;
 for(let row=0;row<totalRows;row++){
   for(let col=0;col<totalCols;col++){
     const x=startX + col*(blockW+blockSpacing);
     const y=startY + row*(blockH+blockSpacing);
     drawPanel(boardChars[row][col],x,y);
     if(row===activeRow && col===activeCol){
       ctx.strokeStyle="#FFD940";
       ctx.lineWidth=2;
       ctx.strokeRect(x-4,y-4,blockW+8,blockH+8);
     }
   }
 }
}
drawBoard();

canvas.addEventListener("click",e=>{
 const rect=canvas.getBoundingClientRect();
 const x=e.clientX-rect.left-40;
 const y=e.clientY-rect.top-40;
 const col=Math.floor(x/(blockW+blockSpacing));
 const row=Math.floor(y/(blockH+blockSpacing));
 activeRow=row;
 activeCol=col;
 drawBoard();
});

document.addEventListener("keydown",e=>{
 if(activeRow>=0 && activeCol>=0){
   let key=e.key.toUpperCase();
   if(FONT[key]){boardChars[activeRow][activeCol]=key;}
   else if(key===" "||key==="BACKSPACE"){boardChars[activeRow][activeCol]=" ";}
   else if(key==="ARROWRIGHT"){activeCol=Math.min(totalCols-1,activeCol+1);}
   else if(key==="ARROWLEFT"){activeCol=Math.max(0,activeCol-1);}
   else if(key==="ARROWDOWN"){activeRow=Math.min(totalRows-1,activeRow+1);}
   else if(key==="ARROWUP"){activeRow=Math.max(0,activeRow-1);}
   drawBoard();
 }
});
</script>
"""
components.html(html_code,height=600)
