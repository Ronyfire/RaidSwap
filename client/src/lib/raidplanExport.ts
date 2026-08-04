export interface RaidPlanExportToken {
  x: number;
  y: number;
  label: string;
  color: string;
}

// Native Canvas, not html2canvas — the content is simple enough (one
// background image + colored text pills) that a real dependency wasn't
// worth adding for it.
export function drawRaidPlanImage(
  canvas: HTMLCanvasElement,
  image: HTMLImageElement,
  tokens: RaidPlanExportToken[],
  width: number,
  height: number,
): void {
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  ctx.drawImage(image, 0, 0, width, height);

  ctx.font = "bold 20px sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  const paddingX = 12;
  const pillHeight = 32;

  for (const token of tokens) {
    const textWidth = ctx.measureText(token.label).width;
    const pillWidth = textWidth + paddingX * 2;
    const left = token.x - pillWidth / 2;
    const top = token.y - pillHeight / 2;

    ctx.fillStyle = token.color;
    ctx.beginPath();
    ctx.roundRect(left, top, pillWidth, pillHeight, pillHeight / 2);
    ctx.fill();

    ctx.fillStyle = "white";
    ctx.fillText(token.label, token.x, token.y + 1);
  }
}

export function downloadCanvasAsPng(canvas: HTMLCanvasElement, filename: string): void {
  canvas.toBlob((blob) => {
    if (!blob) return;
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }, "image/png");
}
