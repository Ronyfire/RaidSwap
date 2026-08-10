export interface RaidPlanExportToken {
  x: number;
  y: number;
  label: string;
  color: string;
  iconUrl?: string | null;
}

function loadImage(url: string): Promise<HTMLImageElement | null> {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => resolve(img);
    // A broken/CORS-blocked icon shouldn't fail the whole export — just
    // draw that one token without its icon.
    img.onerror = () => resolve(null);
    img.src = url;
  });
}

// Native Canvas, not html2canvas — the content is simple enough (one
// background image + colored text pills, optionally a small class icon)
// that a real dependency wasn't worth adding for it.
export async function drawRaidPlanImage(
  canvas: HTMLCanvasElement,
  image: HTMLImageElement,
  tokens: RaidPlanExportToken[],
  width: number,
  height: number,
): Promise<void> {
  const icons = await Promise.all(
    tokens.map((token) => (token.iconUrl ? loadImage(token.iconUrl) : Promise.resolve(null))),
  );

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
  const iconSize = 22;
  const iconGap = 6;

  tokens.forEach((token, i) => {
    const icon = icons[i];
    const textWidth = ctx.measureText(token.label).width;
    const iconSpace = icon ? iconSize + iconGap : 0;
    const pillWidth = textWidth + iconSpace + paddingX * 2;
    const left = token.x - pillWidth / 2;
    const top = token.y - pillHeight / 2;

    ctx.fillStyle = token.color;
    ctx.beginPath();
    ctx.roundRect(left, top, pillWidth, pillHeight, pillHeight / 2);
    ctx.fill();

    ctx.fillStyle = "white";
    const textX = left + paddingX + iconSpace + textWidth / 2;
    ctx.fillText(token.label, textX, token.y + 1);

    if (icon) {
      const iconX = left + paddingX;
      const iconY = token.y - iconSize / 2;
      ctx.save();
      ctx.beginPath();
      ctx.arc(iconX + iconSize / 2, token.y, iconSize / 2, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(icon, iconX, iconY, iconSize, iconSize);
      ctx.restore();
    }
  });
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
