/**
 * result-share.js — Instagram 向けシェア画像（1080×1920）
 * ダークグラデーション・ストーリーカード（画面表示とは別デザイン）
 */

const ResultShare = {
    WIDTH: 1080,
    HEIGHT: 1920,
    APP_NAME: "HIRONOMATCH",
    FONT: '"Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif',

    COLORS: {
        white: "#ffffff",
        category: "rgba(255, 255, 255, 0.72)",
        tagline: "rgba(255, 255, 255, 0.94)",
        desc: "rgba(255, 255, 255, 0.78)",
        footerLoc: "rgba(255, 255, 255, 0.68)",
        footerTags: "rgba(255, 255, 255, 0.82)",
        tagFill: "rgba(255, 255, 255, 0.14)",
        tagBorder: "rgba(255, 255, 255, 0.28)",
        divider: "rgba(255, 255, 255, 0.14)",
    },

    LAYOUT: {
        padX: 144,
        headerTop: 112,
        footerBottomPad: 40,
        footerBlockHeight: 108,
        gapMainToFooter: 52,
        headerToMainMin: 160,
        mainPreferredY: 1040,
        mainGapAfterSubtitle: 12,
        mainGapAfterTitle: 22,
        mainGapAfterTagline: 16,
        mainGapAfterDesc: 20,
        mainLineGap: 6,
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

        this.drawPhoto(ctx, heroImage);
        this.drawGradient(ctx);
        this.drawBrand(ctx);
        this.drawContent(ctx, data);
        this.drawFooter(ctx, data);

        return canvas;
    },

    loadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = "anonymous";
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = src;
        });
    },

    drawPhoto(ctx, img) {
        this.drawCover(ctx, img, 0, 0, this.WIDTH, this.HEIGHT, 0.14);
    },

    drawGradient(ctx) {
        const topG = ctx.createLinearGradient(0, 0, 0, 520);
        topG.addColorStop(0, "rgba(18, 20, 30, 0.48)");
        topG.addColorStop(0.55, "rgba(18, 20, 30, 0.1)");
        topG.addColorStop(1, "rgba(18, 20, 30, 0)");
        ctx.fillStyle = topG;
        ctx.fillRect(0, 0, this.WIDTH, this.HEIGHT);

        const scrimStart = this.HEIGHT * 0.36;
        const bottomG = ctx.createLinearGradient(0, scrimStart, 0, this.HEIGHT);
        bottomG.addColorStop(0, "rgba(10, 12, 20, 0)");
        bottomG.addColorStop(0.28, "rgba(10, 12, 20, 0.42)");
        bottomG.addColorStop(0.52, "rgba(8, 10, 18, 0.72)");
        bottomG.addColorStop(0.76, "rgba(6, 8, 16, 0.88)");
        bottomG.addColorStop(1, "rgba(4, 6, 14, 0.94)");
        ctx.fillStyle = bottomG;
        ctx.fillRect(0, scrimStart, this.WIDTH, this.HEIGHT - scrimStart);
    },

    getFooterTop() {
        return this.HEIGHT - this.LAYOUT.footerBottomPad - this.LAYOUT.footerBlockHeight;
    },

    drawBrand(ctx) {
        ctx.textAlign = "left";
        ctx.textBaseline = "alphabetic";
        ctx.fillStyle = "rgba(255, 255, 255, 0.92)";
        ctx.font = `700 26px ${this.FONT}`;
        ctx.fillText(this.APP_NAME, this.LAYOUT.padX, this.LAYOUT.headerTop);
    },

    getMetrics(ctx, text, font) {
        ctx.font = font;
        const size = Number.parseInt(font, 10) || 24;
        const metrics = ctx.measureText(text);
        const ascent = metrics.actualBoundingBoxAscent ?? size * 0.85;
        const descent = metrics.actualBoundingBoxDescent ?? size * 0.15;
        return {
            width: metrics.width,
            ascent,
            descent,
            height: ascent + descent,
        };
    },

    drawTextLine(ctx, text, x, topY, font, color) {
        const metrics = this.getMetrics(ctx, text, font);
        ctx.font = font;
        ctx.fillStyle = color;
        ctx.textAlign = "left";
        ctx.textBaseline = "alphabetic";
        ctx.fillText(text, x, topY + metrics.ascent);
        return metrics.height;
    },

    drawContent(ctx, data) {
        const pad = this.LAYOUT.padX;
        const maxWidth = this.WIDTH - pad * 2;
        const footerTop = this.getFooterTop();
        const mainBottom = footerTop - this.LAYOUT.gapMainToFooter;

        const subtitleFont = `600 24px ${this.FONT}`;
        const titleFont = `600 72px ${this.FONT}`;
        const taglineFont = `500 38px ${this.FONT}`;
        const descFont = `400 30px ${this.FONT}`;
        const tagFont = `600 24px ${this.FONT}`;
        const tagHeight = 44;
        const lineGap = this.LAYOUT.mainLineGap;

        const blocks = [];

        blocks.push({
            height: this.getMetrics(ctx, data.appSubtitle.toUpperCase(), subtitleFont).height,
            gapBefore: 0,
            draw: (x, topY) => {
                this.drawTextLine(
                    ctx,
                    data.appSubtitle.toUpperCase(),
                    x,
                    topY,
                    subtitleFont,
                    this.COLORS.category,
                );
            },
        });

        ctx.font = titleFont;
        const titleLines = this.splitTypeNameLines(ctx, data.typeName, maxWidth, data.lang);
        let titleHeight = 0;
        titleLines.forEach((line, index) => {
            titleHeight += this.getMetrics(ctx, line, titleFont).height;
            if (index > 0) titleHeight += lineGap;
        });
        blocks.push({
            height: titleHeight,
            gapBefore: this.LAYOUT.mainGapAfterSubtitle,
            draw: (x, topY) => {
                let y = topY;
                titleLines.forEach((line, index) => {
                    if (index > 0) y += lineGap;
                    y += this.drawTextLine(ctx, line, x, y, titleFont, this.COLORS.white);
                });
            },
        });

        if (data.tagline) {
            ctx.font = taglineFont;
            const tagLines = this.wrapText(ctx, data.tagline, maxWidth, 2, data.lang === "en");
            let taglineHeight = 0;
            tagLines.forEach((line, index) => {
                taglineHeight += this.getMetrics(ctx, line, taglineFont).height;
                if (index > 0) taglineHeight += lineGap;
            });
            blocks.push({
                height: taglineHeight,
                gapBefore: this.LAYOUT.mainGapAfterTitle,
                draw: (x, topY) => {
                    let y = topY;
                    tagLines.forEach((line, index) => {
                        if (index > 0) y += lineGap;
                        y += this.drawTextLine(ctx, line, x, y, taglineFont, this.COLORS.tagline);
                    });
                },
            });
        }

        ctx.font = descFont;
        const descLines = this.wrapText(ctx, data.description || "", maxWidth, 3, data.lang === "en");
        let descHeight = 0;
        descLines.forEach((line, index) => {
            descHeight += this.getMetrics(ctx, line, descFont).height;
            if (index > 0) descHeight += lineGap;
        });
        blocks.push({
            height: descHeight,
            gapBefore: data.tagline ? this.LAYOUT.mainGapAfterTagline : this.LAYOUT.mainGapAfterTitle,
            draw: (x, topY) => {
                let y = topY;
                descLines.forEach((line, index) => {
                    if (index > 0) y += lineGap;
                    y += this.drawTextLine(ctx, line, x, y, descFont, this.COLORS.desc);
                });
            },
        });

        const tags = Array.isArray(data.tags) ? data.tags.slice(0, 3) : [];
        if (tags.length) {
            blocks.push({
                height: tagHeight,
                gapBefore: this.LAYOUT.mainGapAfterDesc,
                draw: (x, topY) => {
                    let tagX = x;
                    tags.forEach((tag) => {
                        const metrics = this.getMetrics(ctx, tag, tagFont);
                        const tw = metrics.width + 48;
                        if (tagX + tw > this.WIDTH - pad) return;

                        ctx.fillStyle = this.COLORS.tagFill;
                        ctx.strokeStyle = this.COLORS.tagBorder;
                        ctx.lineWidth = 2;
                        this.roundRect(ctx, tagX, topY, tw, tagHeight, 22);
                        ctx.fill();
                        ctx.stroke();

                        this.drawTextLine(ctx, tag, tagX + 24, topY + 6, tagFont, this.COLORS.white);
                        tagX += tw + 16;
                    });
                },
            });
        }

        let totalHeight = 0;
        blocks.forEach((block) => {
            totalHeight += block.gapBefore + block.height;
        });

        const headerBottom = this.LAYOUT.headerTop + 36;
        let startY = this.LAYOUT.mainPreferredY;
        if (startY + totalHeight > mainBottom) {
            startY = mainBottom - totalHeight;
        }
        if (startY < headerBottom + this.LAYOUT.headerToMainMin) {
            startY = headerBottom + this.LAYOUT.headerToMainMin;
        }

        let y = startY;
        blocks.forEach((block) => {
            y += block.gapBefore;
            block.draw(pad, y);
            y += block.height;
        });
    },

    drawFooter(ctx, data) {
        const pad = this.LAYOUT.padX;
        const centerX = this.WIDTH / 2;
        const bottomPad = this.LAYOUT.footerBottomPad;
        const footerTop = this.getFooterTop();

        ctx.strokeStyle = this.COLORS.divider;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(pad, footerTop);
        ctx.lineTo(this.WIDTH - pad, footerTop);
        ctx.stroke();

        ctx.textAlign = "center";
        ctx.textBaseline = "alphabetic";

        const brandY = footerTop + 36;
        ctx.fillStyle = this.COLORS.white;
        ctx.font = `700 24px ${this.FONT}`;
        ctx.fillText(this.APP_NAME, centerX, brandY);

        ctx.fillStyle = this.COLORS.footerLoc;
        ctx.font = `500 22px ${this.FONT}`;
        ctx.fillText(data.location, centerX, brandY + 28);

        ctx.fillStyle = this.COLORS.footerTags;
        ctx.font = `600 20px ${this.FONT}`;
        const tagsY = this.HEIGHT - bottomPad;
        ctx.fillText(data.hashtags, centerX, tagsY);
    },

    splitTypeNameLines(ctx, typeName, maxWidth, lang) {
        if (ctx.measureText(typeName).width <= maxWidth) {
            return [typeName];
        }
        if (lang === "en") {
            return this.wrapText(ctx, typeName, maxWidth, 2, true);
        }
        if (typeName.includes("シーサイド") && typeName.endsWith("リラックス")) {
            return ["シーサイド", "リラックス"];
        }
        for (let i = 2; i <= typeName.length - 2; i += 1) {
            const a = typeName.slice(0, i);
            const b = typeName.slice(i);
            if (ctx.measureText(a).width <= maxWidth && ctx.measureText(b).width <= maxWidth) {
                return [a, b];
            }
        }
        return this.wrapText(ctx, typeName, maxWidth, 2, false);
    },

    wrapText(ctx, text, maxWidth, maxLines, byWord) {
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
        if (current.trim()) lines.push(current.trim());
        return lines.slice(0, maxLines);
    },

    roundRect(ctx, x, y, w, h, r) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + w - r, y);
        ctx.quadraticCurveTo(x + w, y, x + w, y + r);
        ctx.lineTo(x + w, y + h - r);
        ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
        ctx.lineTo(x + r, y + h);
        ctx.quadraticCurveTo(x, y + h, x, y + h - r);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.closePath();
    },

    drawCover(ctx, img, x, y, w, h, focalBias = 0.5) {
        const scale = Math.max(w / img.width, h / img.height);
        const dw = img.width * scale;
        const dh = img.height * scale;
        const dx = x + (w - dw) / 2;
        const dy = y + (h - dh) * focalBias;
        ctx.drawImage(img, dx, dy, dw, dh);
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
