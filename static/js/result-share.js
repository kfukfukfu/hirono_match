/**
 * result-share.js — Instagram Stories シェア画像（1080×1920）
 * 「旅の表紙」エディトリアルデザイン
 */

const ResultShare = {
    WIDTH: 1080,
    HEIGHT: 1920,
    APP_NAME: "HIRONOMATCH",
    FONT: '"Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif',

    COLORS: {
        cream: "#fef3c7",
        gold: "#e8c468",
        goldDeep: "#c9a227",
        white: "#ffffff",
        muted: "rgba(255, 255, 255, 0.72)",
        soft: "rgba(255, 255, 255, 0.88)",
        footer: "rgba(255, 255, 255, 0.55)",
        tagPrimary: "rgba(232, 196, 104, 0.92)",
        tagPrimaryText: "#1a1408",
        tagGhost: "rgba(255, 255, 255, 0.14)",
        tagGhostBorder: "rgba(255, 255, 255, 0.32)",
    },

    TYPOGRAPHY: {
        brand: 24,
        label: 18,
        category: 20,
        title: 100,
        tagline: 38,
        desc: 27,
        tag: 22,
        footer: 21,
    },

    LAYOUT: {
        padX: 56,
        headerTop: 72,
        accentBarW: 5,
        accentBarH: 52,
        contentBottom: 108,
        footerBottom: 52,
        gapLabelToCategory: 28,
        gapCategoryToTitle: 14,
        gapTitleToTagline: 18,
        gapTaglineToDesc: 22,
        gapDescToTags: 28,
        titleLineGap: 4,
        tagHeight: 46,
        tagPadX: 26,
        tagGap: 12,
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
        const labelEl = shareBtn?.querySelector("[data-share-label]");
        const teaser = container.querySelector(".result-share-teaser");
        const defaultLabel = labelEl?.textContent?.trim() || shareBtn?.textContent?.trim() || "";

        const setStatus = (message, isError = false) => {
            if (!statusEl) return;
            statusEl.textContent = message;
            statusEl.hidden = !message;
            statusEl.classList.toggle("result-share-status-error", isError);
        };

        const setGenerating = (isGenerating) => {
            if (!shareBtn) return;
            shareBtn.disabled = isGenerating;
            const text = isGenerating ? data.labels.generating : defaultLabel;
            if (labelEl) {
                labelEl.textContent = text;
            } else {
                shareBtn.textContent = text;
            }
        };

        shareBtn?.addEventListener("click", async () => {
            setGenerating(true);
            setStatus("");

            try {
                const canvas = await this.generate(data);
                if (preview) {
                    preview.src = canvas.toDataURL("image/png");
                    preview.hidden = false;
                    preview.closest(".result-share-preview-wrap")?.classList.add("is-visible");
                    teaser?.classList.add("is-hidden");
                }
                this.download(canvas, data.filename);
                setStatus(data.labels.success);
            } catch {
                setStatus(data.labels.error, true);
            } finally {
                setGenerating(false);
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
        this.drawOverlays(ctx);
        this.drawHeader(ctx);
        this.drawMainContent(ctx, data);
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
        this.drawCover(ctx, img, 0, 0, this.WIDTH, this.HEIGHT, 0.34);
    },

    drawOverlays(ctx) {
        const top = ctx.createLinearGradient(0, 0, 0, 420);
        top.addColorStop(0, "rgba(0, 0, 0, 0.48)");
        top.addColorStop(1, "rgba(0, 0, 0, 0)");
        ctx.fillStyle = top;
        ctx.fillRect(0, 0, this.WIDTH, 420);

        const scrimStart = this.HEIGHT * 0.48;
        const bottom = ctx.createLinearGradient(0, scrimStart, 0, this.HEIGHT);
        bottom.addColorStop(0, "rgba(0, 0, 0, 0)");
        bottom.addColorStop(0.25, "rgba(0, 0, 0, 0.35)");
        bottom.addColorStop(0.55, "rgba(0, 0, 0, 0.72)");
        bottom.addColorStop(1, "rgba(0, 0, 0, 0.88)");
        ctx.fillStyle = bottom;
        ctx.fillRect(0, scrimStart, this.WIDTH, this.HEIGHT - scrimStart);

        const warm = ctx.createRadialGradient(
            this.WIDTH * 0.15,
            this.HEIGHT * 0.82,
            0,
            this.WIDTH * 0.15,
            this.HEIGHT * 0.82,
            this.WIDTH * 0.55,
        );
        warm.addColorStop(0, "rgba(201, 162, 39, 0.07)");
        warm.addColorStop(1, "rgba(0, 0, 0, 0)");
        ctx.fillStyle = warm;
        ctx.fillRect(0, scrimStart, this.WIDTH, this.HEIGHT - scrimStart);
    },

    drawHeader(ctx) {
        const pad = this.LAYOUT.padX;
        const y = this.LAYOUT.headerTop;

        ctx.textAlign = "left";
        ctx.textBaseline = "alphabetic";
        ctx.fillStyle = "rgba(255, 255, 255, 0.88)";
        ctx.font = this.font(700, this.TYPOGRAPHY.brand);
        this.drawTrackedText(ctx, this.APP_NAME, pad, y, this.TYPOGRAPHY.brand * 0.22);

        ctx.strokeStyle = "rgba(232, 196, 104, 0.55)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(pad, y + 14);
        ctx.lineTo(pad + 72, y + 14);
        ctx.stroke();
    },

    measureContent(ctx, data, maxWidth) {
        const titleFont = this.font(900, this.TYPOGRAPHY.title);
        const taglineFont = this.font(600, this.TYPOGRAPHY.tagline);
        const descFont = this.font(400, this.TYPOGRAPHY.desc);
        const categoryFont = this.font(600, this.TYPOGRAPHY.category);

        ctx.font = titleFont;
        const titleLines = this.splitTypeNameLines(ctx, data.typeName, maxWidth, data.lang);
        let h = this.LAYOUT.accentBarH + this.LAYOUT.gapLabelToCategory;
        h += this.getMetrics(ctx, data.appSubtitle.toUpperCase(), categoryFont).height;
        h += this.LAYOUT.gapCategoryToTitle;
        titleLines.forEach((line, i) => {
            h += this.getMetrics(ctx, line, titleFont).height;
            if (i > 0) h += this.LAYOUT.titleLineGap;
        });

        let taglineLines = [];
        if (data.tagline) {
            ctx.font = taglineFont;
            taglineLines = this.wrapText(ctx, data.tagline, maxWidth, 2, data.lang === "en");
            h += this.LAYOUT.gapTitleToTagline;
            taglineLines.forEach((line, i) => {
                h += this.getMetrics(ctx, line, taglineFont).height;
                if (i > 0) h += 6;
            });
        }

        ctx.font = descFont;
        const descLines = this.wrapText(ctx, data.description || "", maxWidth, 2, data.lang === "en");
        h += data.tagline ? this.LAYOUT.gapTaglineToDesc : this.LAYOUT.gapTitleToTagline;
        descLines.forEach((line, i) => {
            h += this.getMetrics(ctx, line, descFont).height;
            if (i > 0) h += 8;
        });

        const tags = Array.isArray(data.tags) ? data.tags.slice(0, 3) : [];
        if (tags.length) h += this.LAYOUT.gapDescToTags + this.LAYOUT.tagHeight;

        return { titleLines, taglineLines, descLines, tags, totalHeight: h };
    },

    drawMainContent(ctx, data) {
        const pad = this.LAYOUT.padX;
        const textX = pad + this.LAYOUT.accentBarW + 20;
        const maxWidth = this.WIDTH - textX - pad;
        const footerReserve = this.LAYOUT.footerBottom + 56;
        const content = this.measureContent(ctx, data, maxWidth);

        let blockTop = this.HEIGHT - this.LAYOUT.contentBottom - footerReserve - content.totalHeight;
        if (blockTop < 200) blockTop = 200;

        const barX = pad;
        const barY = blockTop;
        const barGrad = ctx.createLinearGradient(barX, barY, barX, barY + this.LAYOUT.accentBarH);
        barGrad.addColorStop(0, this.COLORS.gold);
        barGrad.addColorStop(1, this.COLORS.goldDeep);
        ctx.fillStyle = barGrad;
        ctx.fillRect(barX, barY, this.LAYOUT.accentBarW, this.LAYOUT.accentBarH);

        let y = blockTop + this.LAYOUT.gapLabelToCategory;
        const categoryFont = this.font(600, this.TYPOGRAPHY.category);
        y += this.drawGlowText(
            ctx,
            data.appSubtitle.toUpperCase(),
            textX,
            y,
            categoryFont,
            this.COLORS.gold,
            4,
        );

        y += this.LAYOUT.gapCategoryToTitle;
        const titleFont = this.font(900, this.TYPOGRAPHY.title);
        content.titleLines.forEach((line, index) => {
            if (index > 0) y += this.LAYOUT.titleLineGap;
            y += this.drawGlowText(ctx, line, textX, y, titleFont, this.COLORS.white, 10);
        });

        if (content.taglineLines.length) {
            y += this.LAYOUT.gapTitleToTagline;
            const taglineFont = this.font(600, this.TYPOGRAPHY.tagline);
            content.taglineLines.forEach((line, index) => {
                if (index > 0) y += 6;
                y += this.drawGlowText(ctx, line, textX, y, taglineFont, this.COLORS.cream, 6);
            });
        }

        y += content.taglineLines.length
            ? this.LAYOUT.gapTaglineToDesc
            : this.LAYOUT.gapTitleToTagline;
        const descFont = this.font(400, this.TYPOGRAPHY.desc);
        content.descLines.forEach((line, index) => {
            if (index > 0) y += 8;
            y += this.drawGlowText(ctx, line, textX, y, descFont, this.COLORS.soft, 4);
        });

        if (content.tags.length) {
            y += this.LAYOUT.gapDescToTags;
            let tagX = textX;
            content.tags.forEach((tag, index) => {
                const tagFont = this.font(600, this.TYPOGRAPHY.tag);
                ctx.font = tagFont;
                const tw = ctx.measureText(tag).width + this.LAYOUT.tagPadX * 2;
                const th = this.LAYOUT.tagHeight;
                const isPrimary = index === 0;

                this.roundRect(ctx, tagX, y, tw, th, th / 2);
                if (isPrimary) {
                    ctx.fillStyle = this.COLORS.tagPrimary;
                    ctx.fill();
                    this.drawTextLine(ctx, tag, tagX + this.LAYOUT.tagPadX, y + 7, tagFont, this.COLORS.tagPrimaryText);
                } else {
                    ctx.fillStyle = this.COLORS.tagGhost;
                    ctx.fill();
                    ctx.strokeStyle = this.COLORS.tagGhostBorder;
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    this.drawTextLine(ctx, tag, tagX + this.LAYOUT.tagPadX, y + 7, tagFont, this.COLORS.white);
                }
                tagX += tw + this.LAYOUT.tagGap;
            });
        }
    },

    drawFooter(ctx, data) {
        const y = this.HEIGHT - this.LAYOUT.footerBottom;
        const loc = this.shortLocation(data.location);
        const tags = data.hashtags || "#HIRONOMATCH";
        const line = `${loc}  ·  ${tags}`;

        ctx.textAlign = "center";
        ctx.textBaseline = "alphabetic";
        ctx.fillStyle = this.COLORS.footer;
        ctx.font = this.font(500, this.TYPOGRAPHY.footer);
        ctx.fillText(line, this.WIDTH / 2, y);
    },

    shortLocation(location) {
        if (!location) return "Hirono, Iwate";
        return location.replace(" Japan JP", "").replace(" JP", "");
    },

    font(weight, size) {
        return `${weight} ${size}px ${this.FONT}`;
    },

    drawTrackedText(ctx, text, x, baselineY, tracking) {
        ctx.textAlign = "left";
        ctx.textBaseline = "alphabetic";
        let cursorX = x;
        [...text].forEach((char) => {
            ctx.fillText(char, cursorX, baselineY);
            cursorX += ctx.measureText(char).width + tracking;
        });
    },

    getMetrics(ctx, text, font) {
        ctx.font = font;
        const size = Number.parseInt(font, 10) || 24;
        const metrics = ctx.measureText(text);
        const ascent = metrics.actualBoundingBoxAscent ?? size * 0.85;
        const descent = metrics.actualBoundingBoxDescent ?? size * 0.15;
        return { width: metrics.width, ascent, descent, height: ascent + descent };
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

    drawGlowText(ctx, text, x, topY, font, color, blur) {
        const metrics = this.getMetrics(ctx, text, font);
        ctx.font = font;
        ctx.textAlign = "left";
        ctx.textBaseline = "alphabetic";
        const baseline = topY + metrics.ascent;

        ctx.save();
        ctx.shadowColor = "rgba(0, 0, 0, 0.55)";
        ctx.shadowBlur = blur;
        ctx.shadowOffsetY = 2;
        ctx.fillStyle = color;
        ctx.fillText(text, x, baseline);
        ctx.restore();

        return metrics.height;
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
