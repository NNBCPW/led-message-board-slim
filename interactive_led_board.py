import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Interactive LED Board", layout="centered")

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .main {
    background: #141414 !important;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 1000px;
}

.led-wrap {
    width: 100%;
    display: flex;
    justify-content: center;
}

iframe {
    border: 0 !important;
}
</style>
""", unsafe_allow_html=True)

html_code = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<style>
    :root{
        --bg:#141414;
        --panel:#181818;
        --tile-border:#222222;
        --led-on:#F9ED32;
        --led-off:#3B3C3D;
        --active:#4a4a4a;
        --text:#f2f2f2;
        --btn:#F9ED32;
        --btn-text:#111111;
    }

    * { box-sizing: border-box; }

    html, body {
        margin: 0;
        padding: 0;
        background: var(--bg);
        color: var(--text);
        font-family: Arial, Helvetica, sans-serif;
    }

    .app {
        width: 100%;
        max-width: 980px;
        margin: 0 auto;
        padding: 12px;
    }

    .board-shell {
        background: var(--bg);
        border-radius: 16px;
        padding: 10px;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }

    canvas {
        background: var(--bg);
        display: block;
        margin: 0 auto;
        border-radius: 12px;
        box-shadow: inset 0 0 30px #000;
        touch-action: manipulation;
        max-width: 100%;
        height: auto;
    }

    .controls {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        margin-top: 14px;
    }

    button {
        appearance: none;
        border: none;
        border-radius: 12px;
        padding: 14px 18px;
        font-size: 16px;
        font-weight: 700;
        cursor: pointer;
        min-height: 48px;
    }

    .primary {
        background: var(--btn);
        color: var(--btn-text);
    }

    .secondary {
        background: #2a2a2a;
        color: #ffffff;
    }

    .help {
        margin-top: 12px;
        text-align: center;
        color: #bdbdbd;
        font-size: 14px;
        line-height: 1.4;
    }

    .mobile-pad {
        display: none;
        margin-top: 12px;
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
    }

    .mobile-pad button {
        min-width: 60px;
        padding: 14px 16px;
    }

    .spacer {
        flex-basis: 100%;
        height: 0;
    }

    @media (max-width: 768px) {
        .app {
            padding: 8px;
        }

        .controls {
            gap: 8px;
        }

        button {
            width: 100%;
        }

        .mobile-pad {
            display: flex;
        }

        .mobile-pad button.small {
            width: calc(33.333% - 6px);
            min-width: unset;
        }

        .mobile-pad button.wide {
            width: calc(66.666% - 6px);
            min-width: unset;
        }
    }
</style>
</head>
<body>
<div class="app">
    <div class="board-shell">
        <canvas id="ledBoard"></canvas>
    </div>

    <div class="controls">
        <button class="primary" id="downloadBtn">Download Image (PNG)</button>
        <button class="secondary" id="clearBtn">Clear Board</button>
    </div>

    <div class="mobile-pad">
        <button class="small secondary" data-key="←">←</button>
        <button class="small secondary" data-key="→">→</button>
        <button class="small secondary" data-key="↵">↵</button>
        <button class="wide secondary" data-key="SPACE">Space</button>
        <button class="small secondary" data-key="⌫">⌫</button>
    </div>

    <div class="help">
        Tap any tile to type. The active tile is shown while editing, but the PNG download saves without the highlight box.
    </div>
</div>

<script>
// ---------- COLORS ----------
const LED_ON   = "#F9ED32";
const LED_OFF  = "#3B3C3D";
const BG_COLOR = "#141414";
const GAP_LINE = "#222222";
const ACTIVE_COLOR = "#4a4a4a";

// ---------- GRID ----------
const ROWS = 4, COLS = 10;
const DOT_W = 5, DOT_H = 7;
const DOT_SIZE = 10, DOT_GAP = 4;
const TILE_PAD = 6, TILE_GAP = 6, OUTER_PAD = 10;

// ---------- GEOMETRY ----------
function tileW(){ return DOT_W * DOT_SIZE + (DOT_W - 1) * DOT_GAP + 2 * TILE_PAD; }
function tileH(){ return DOT_H * DOT_SIZE + (DOT_H - 1) * DOT_GAP + 2 * TILE_PAD; }
const TW = tileW(), TH = tileH();
const BOARD_W = OUTER_PAD * 2 + COLS * TW + (COLS - 1) * TILE_GAP;
const BOARD_H = OUTER_PAD * 2 + ROWS * TH + (ROWS - 1) * TILE_GAP;

// ---------- FONT ----------
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
let chars = Array.from({length: ROWS}, () => Array(COLS).fill(" "));
let active = { r: 0, c: 0 };

// ---------- CANVAS ----------
const canvas = document.getElementById("ledBoard");
const ctx = canvas.getContext("2d", { alpha: false });

function setupCanvas() {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(BOARD_W * dpr);
    canvas.height = Math.round(BOARD_H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const shellWidth = document.querySelector(".board-shell").clientWidth - 20;
    const cssWidth = Math.min(shellWidth, BOARD_W);
    canvas.style.width = cssWidth + "px";
    canvas.style.height = (BOARD_H * cssWidth / BOARD_W) + "px";

    drawBoard(true);
}

// ---------- DRAW ----------
function drawDot(x, y, on) {
    ctx.beginPath();
    ctx.arc(x + DOT_SIZE / 2, y + DOT_SIZE / 2, DOT_SIZE / 2, 0, Math.PI * 2);
    ctx.fillStyle = on ? LED_ON : LED_OFF;
    ctx.fill();
}

function drawTile(ch, x, y) {
    ctx.fillStyle = BG_COLOR;
    ctx.fillRect(x, y, TW, TH);

    ctx.strokeStyle = GAP_LINE;
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, TW, TH);

    const p = FONT[ch] || FONT[" "];
    const sx = x + TILE_PAD;
    const sy = y + TILE_PAD;

    for (let gy = 0; gy < DOT_H; gy++) {
        for (let gx = 0; gx < DOT_W; gx++) {
            const on = p[gy][gx] === "1";
            drawDot(sx + gx * (DOT_SIZE + DOT_GAP), sy + gy * (DOT_SIZE + DOT_GAP), on);
        }
    }
}

function drawBoard(showActive = true) {
    ctx.fillStyle = BG_COLOR;
    ctx.fillRect(0, 0, BOARD_W, BOARD_H);

    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            const x = OUTER_PAD + c * (TW + TILE_GAP);
            const y = OUTER_PAD + r * (TH + TILE_GAP);

            drawTile(chars[r][c], x, y);

            if (showActive && active.r === r && active.c === c) {
                ctx.lineWidth = 2;
                ctx.strokeStyle = ACTIVE_COLOR;
                ctx.strokeRect(x - 1, y - 1, TW + 2, TH + 2);
            }
        }
    }
}

// ---------- INPUT ----------
const hiddenInput = document.createElement("input");
hiddenInput.type = "text";
hiddenInput.autocapitalize = "characters";
hiddenInput.autocomplete = "off";
hiddenInput.spellcheck = false;
hiddenInput.style.position = "fixed";
hiddenInput.style.opacity = "0";
hiddenInput.style.pointerEvents = "none";
hiddenInput.style.bottom = "0";
hiddenInput.style.left = "0";
hiddenInput.style.width = "1px";
hiddenInput.style.height = "1px";
document.body.appendChild(hiddenInput);

function focusInput() {
    hiddenInput.focus();
}

function setActiveFromPointer(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = BOARD_W / rect.width;
    const scaleY = BOARD_H / rect.height;
    const mx = (clientX - rect.left) * scaleX;
    const my = (clientY - rect.top) * scaleY;

    const x = mx - OUTER_PAD;
    const y = my - OUTER_PAD;

    const col = Math.floor(x / (TW + TILE_GAP));
    const row = Math.floor(y / (TH + TILE_GAP));

    if (row >= 0 && row < ROWS && col >= 0 && col < COLS) {
        active = { r: row, c: col };
        drawBoard(true);
        focusInput();
    }
}

canvas.addEventListener("click", (e) => {
    setActiveFromPointer(e.clientX, e.clientY);
});

canvas.addEventListener("touchstart", (e) => {
    const t = e.touches[0];
    if (t) setActiveFromPointer(t.clientX, t.clientY);
}, { passive: true });

// ---------- NAVIGATION ----------
function advance() {
    active.c += 1;
    if (active.c >= COLS) {
        active.c = 0;
        active.r = Math.min(active.r + 1, ROWS - 1);
    }
    drawBoard(true);
}

function moveLeft() {
    if (active.c > 0) {
        active.c -= 1;
    } else if (active.r > 0) {
        active.r -= 1;
        active.c = COLS - 1;
    }
    drawBoard(true);
}

function moveRight() {
    if (active.c < COLS - 1) {
        active.c += 1;
    } else if (active.r < ROWS - 1) {
        active.r += 1;
        active.c = 0;
    }
    drawBoard(true);
}

function nextLine() {
    active.c = 0;
    active.r = Math.min(active.r + 1, ROWS - 1);
    drawBoard(true);
}

function backspace() {
    if (chars[active.r][active.c] !== " ") {
        chars[active.r][active.c] = " ";
    } else if (active.c > 0 || active.r > 0) {
        if (active.c > 0) {
            active.c -= 1;
        } else {
            active.r -= 1;
            active.c = COLS - 1;
        }
        chars[active.r][active.c] = " ";
    }
    drawBoard(true);
}

function insertChar(ch) {
    if (FONT[ch]) {
        chars[active.r][active.c] = ch;
        advance();
    }
}

// ---------- KEYBOARD ----------
document.addEventListener("keydown", (e) => {
    if (e.key === "Backspace") {
        e.preventDefault();
        backspace();
        return;
    }

    if (e.key === "Enter") {
        e.preventDefault();
        nextLine();
        return;
    }

    if (e.key === "ArrowLeft") {
        e.preventDefault();
        moveLeft();
        return;
    }

    if (e.key === "ArrowRight") {
        e.preventDefault();
        moveRight();
        return;
    }

    if (e.key === " ") {
        e.preventDefault();
        advance();
        return;
    }

    if (e.key.length === 1) {
        let ch = e.key.toUpperCase();
        if (FONT[ch]) {
            e.preventDefault();
            insertChar(ch);
        }
    }
});

// ---------- MOBILE PAD ----------
document.querySelectorAll(".mobile-pad button").forEach((btn) => {
    btn.addEventListener("click", () => {
        const key = btn.getAttribute("data-key");
        focusInput();

        if (key === "←") return moveLeft();
        if (key === "→") return moveRight();
        if (key === "↵") return nextLine();
        if (key === "⌫") return backspace();
        if (key === "SPACE") return advance();
    });
});

// ---------- ACTIONS ----------
document.getElementById("clearBtn").addEventListener("click", () => {
    chars = Array.from({length: ROWS}, () => Array(COLS).fill(" "));
    active = { r: 0, c: 0 };
    drawBoard(true);
    focusInput();
});

document.getElementById("downloadBtn").addEventListener("click", () => {
    drawBoard(false);

    const link = document.createElement("a");
    link.download = "led-board.png";
    link.href = canvas.toDataURL("image/png");
    link.click();

    drawBoard(true);
    focusInput();
});

window.addEventListener("resize", setupCanvas);

// ---------- INIT ----------
setupCanvas();
focusInput();
</script>
</body>
</html>
"""

components.html(html_code, height=720)
st.markdown("---")
st.caption("Created by NN.")
