/**
 * result-share.js
 * ---------------
 * 診断結果を Instagram ストーリーズ向け縦長画像（1080×1920）として生成する。
 * 診断タイプ名を主役にした、投稿したくなるミニマルなシェアカード。
 */

const ResultShare = {
    WIDTH: 1080,
    HEIGHT: 1920,
    APP_NAME: "HIRONOMATCH",
    FONT: '"Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif',

    COLORS: {
        primary: "#1a6b8a",
        primaryDark: "#0f4d66",
        accent: "#f4a261",
        white: "#ffffff",
        sea: "#7ec8e3",
        card: "rgba(255, 255, 255, 0.94)",
    },

    init(containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        const dataEl = document.getElementById("result-share-data");
        if (!dataEl) return;

        let data;
        try {
            data = JSON.parse(dataEl.textContent);
        } catch {
            return;
        }

        const shareBtn = container.querySelector("[data-share-action]");
        const preview = container.querySelector("[data-share-preview]");
        const statusEl = container.querySelector("[data-share-status]");
        const defaultLabel = shareBtn?.textContent?.trim() || "";

        const setStatus = (message, isError = false) => {
            if (!statusEl) return;
            statusEl.textContent = message;
            statusEl.hidden = !message;
            statusEl.classList.toggle("result-share-status-error", isError);
        };

        shareBtn?.addEventListener("click", async () => {
            shareBtn.disabled = true;
            shareBtn.textContent = data.labels.generating;
            setStatus("");

            try {
                const canvas = await this.generate(data);
                if (preview) {
                    preview.src = canvas.toDataURL("image/png");
                    preview.hidden = false;
                    preview.closest(".result-share-preview-wrap")?.classList.add("is-visible");
                }
                this.download(canvas, data.filename);
                setStatus(data.labels.success);
            } catch {
                setStatus(data.labels.error, true);
            } finally {
                shareBtn.disabled = false;
                shareBtn.textContent = defaultLabel;
            }
        });
    },

    async generate(data) {
        const canvas = document.createElement("canvas");
        canvas.width = this.WIDTH;
        canvas.height = this.HEIGHT;
        const ctx = canvas.getContext("2d");
        const heroImage = await this.loadImage(data.imageUrl);

        this.drawPhotoBackground(ctx, heroImage);
        this.drawOverlay(ctx);
        this.drawDecorations(ctx);
        this.drawHeader(ctx, data);
        this.drawTypeCard(ctx, data);
        this.drawFooter(ctx, data);

        return canvas;
    },

    loadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = src;
        });
    },

    drawPhotoBackground(ctx, img) {
        this.drawCoverImage(ctx, img, 0, 0, this.WIDTH, this.HEIGHT);
    },

    drawOverlay(ctx) {
        const gradient = ctx.createLinearGradient(0, 0, 0, this.HEIGHT);
        gradient.addColorStop(0, "rgba(6, 38, 54, 0.72)");
        gradient.addColorStop(0.42, "rgba(15, 77, 102, 0.55)");
        gradient.addColorStop(0.68, "rgba(26, 107, 138, 0.62)");
        gradient.addColorStop(1, "rgba(6, 38, 54, 0.88)");
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, this.WIDTH, this.HEIGHT);
    },

    drawDecorations(ctx) {
        ctx.save();
        ctx.globalAlpha = 0.14;
        ctx.fillStyle = this.COLORS.sea;

        for (let i = 0; i < 3; i += 1) {
            ctx.beginPath();
            const baseY = this.HEIGHT * (0.78 + i * 0.06);
            ctx.moveTo(0, baseY);
            for (let x = 0; x <= this.WIDTH; x += 32) {
                const y = baseY + Math.sin((x / this.WIDTH) * Math.PI * 6 + i * 1.2) * 28;
                ctx.lineTo(x, y);
            }
            ctx.lineTo(this.WIDTH, this.HEIGHT);
            ctx.lineTo(0, this.HEIGHT);
            ctx.closePath();
            ctx.fill();
        }

        ctx.restore();

        ctx.strokeStyle = "rgba(244, 162, 97, 0.55)";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(120, 200);
        ctx.lineTo(240, 200);
        ctx.stroke();
    },

    drawHeader(ctx, data) {
        const centerX = this.WIDTH / 2;

        ctx.textAlign = "center";
        ctx.fillStyle = this.COLORS.white;
        ctx.font = `800 52px ${this.FONT}`;
        ctx.fillText(this.APP_NAME, centerX, 148);

        ctx.fillStyle = "rgba(255, 255, 255, 0.82)";
        ctx.font = `600 28px ${this.FONT}`;
        ctx.fillText(data.appSubtitle.toUpperCase(), centerX, 198);
        ctx.textAlign = "left";
    },

    drawTypeCard(ctx, data) {
        const cardX = 80;
        const cardY = 620;
        const cardW = this.WIDTH - 160;
        const cardH = 560;
        const radius = 40;

        ctx.save();
        ctx.shadowColor = "rgba(6, 38, 54, 0.35)";
        ctx.shadowBlur = 48;
        ctx.shadowOffsetY = 16;
        ctx.fillStyle = this.COLORS.card;
        this.roundRect(ctx, cardX, cardY, cardW, cardH, radius);
        ctx.fill();
        ctx.restore();

        ctx.strokeStyle = "rgba(26, 107, 138, 0.12)";
        ctx.lineWidth = 2;
        this.roundRect(ctx, cardX, cardY, cardW, cardH, radius);
        ctx.stroke();

        const centerX = this.WIDTH / 2;
        ctx.textAlign = "center";

        ctx.font = `700 72px ${this.FONT}`;
        ctx.fillText("🌊", centerX, cardY + 120);

        ctx.fillStyle = this.COLORS.primaryDark;
        ctx.font = `800 108px ${this.FONT}`;
        const titleLines = this.wrapText(
            ctx,
            data.typeName,
            cardW - 100,
            2,
            data.lang === "en"
        );

        let y = cardY + 280;
        titleLines.forEach((line) => {
            ctx.fillText(line, centerX, y);
            y += 118;
        });

        ctx.fillStyle = this.COLORS.accent;
        ctx.fillRect(centerX - 48, cardY + cardH - 56, 96, 6);

        ctx.textAlign = "left";
    },

    drawFooter(ctx, data) {
        const centerX = this.WIDTH / 2;
        const footerY = this.HEIGHT - 220;

        ctx.textAlign = "center";
        ctx.fillStyle = "rgba(255, 255, 255, 0.92)";
        ctx.font = `600 36px ${this.FONT}`;
        ctx.fillText(data.footerLine, centerX, footerY);

        ctx.fillStyle = "rgba(255, 255, 255, 0.72)";
        ctx.font = `500 30px ${this.FONT}`;
        ctx.fillText(data.location, centerX, footerY + 56);

        ctx.fillStyle = "rgba(244, 162, 97, 0.85)";
        ctx.font = `700 24px ${this.FONT}`;
        ctx.fillText(data.hashtags, centerX, footerY + 108);

        ctx.textAlign = "left";
    },

    roundRect(ctx, x, y, width, height, radius) {
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + width - radius, y);
        ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
        ctx.lineTo(x + width, y + height - radius);
        ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        ctx.lineTo(x + radius, y + height);
        ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
        ctx.lineTo(x, y + radius);
        ctx.quadraticCurveTo(x, y, x + radius, y);
        ctx.closePath();
    },

    drawCoverImage(ctx, img, x, y, width, height) {
        const scale = Math.max(width / img.width, height / img.height);
        const drawWidth = img.width * scale;
        const drawHeight = img.height * scale;
        const offsetX = x + (width - drawWidth) / 2;
        const offsetY = y + (height - drawHeight) / 2;
        ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
    },

    wrapText(ctx, text, maxWidth, maxLines, byWord = false) {
        const units = byWord ? text.split(/(\s+)/).filter(Boolean) : [...text];
        const lines = [];
        let current = "";

        units.forEach((unit) => {
            const next = current + unit;
            if (ctx.measureText(next).width > maxWidth && current) {
                lines.push(current.trim());
                current = byWord ? unit.trim() : unit;
            } else {
                current = next;
            }
        });

        if (current.trim()) {
            lines.push(current.trim());
        }

        if (lines.length <= maxLines) {
            return lines;
        }

        const trimmed = lines.slice(0, maxLines);
        const last = trimmed[maxLines - 1];
        trimmed[maxLines - 1] = `${last.replace(/[….]$/, "")}…`;
        return trimmed;
    },

    download(canvas, filename) {
        canvas.toBlob((blob) => {
            if (!blob) return;
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(url);
        }, "image/png");
    },
};

document.addEventListener("DOMContentLoaded", () => {
    ResultShare.init(".result-share");
});
