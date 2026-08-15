/**
 * result-share.js — Instagram 向けシェア画像（1080×1920）
 * 額縁カード + フッター構成（参考モック準拠）
 */

const ResultShare = {
    WIDTH: 1080,
    HEIGHT: 1920,
    APP_NAME: "HIRONOMATCH",
    FONT: '"Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif',

    COLORS: {
        canvas: "#101014",
        cardBorder: "#d9cdb5",
        cardInner: "#121218",
        white: "#ffffff",
        category: "rgba(255, 255, 255, 0.72)",
        tagline: "rgba(255, 255, 255, 0.94)",
        desc: "rgba(255, 255, 255, 0.78)",
        footerLoc: "rgba(255, 255, 255, 0.68)",
        footerTags: "rgba(255, 255, 255, 0.82)",
        tagFill: "rgba(255, 255, 255, 0.14)",
        tagBorder: "rgba(255, 255, 255, 0.28)",
        divider: "rgba(255, 255, 255, 0.14)",
        panelFill: "rgba(20, 22, 30, 0.84)",
        panelStroke: "rgba(255, 255, 255, 0.1)",
    },

    TYPOGRAPHY: {
        header: 30,
        subtitle: 26,
        title: 80,
        tagline: 42,
        desc: 32,
        tag: 26,
        footerBrand: 28,
        footerLoc: 26,
        footerTags: 24,
    },

    LAYOUT: {
        cardMarginX: 72,
        cardMarginTop: 96,
        cardBorder: 12,
        cardPhotoRatio: 0.58,
        cardFooterGap: 64,
        footerBottomPad: 48,
        footerBlockHeight: 118,
        panelInset: 36,
        panelPad: 44,
        panelRadius: 24,
        panelPhotoOverlap: 56,
        logoInsetX: 40,
        logoInsetY: 44,
        mainGapAfterSubtitle: 14,
        mainGapAfterTitle: 24,
        mainGapAfterTagline: 18,
        mainGapAfterDesc: 22,
        mainLineGap: 8,
        tagHeight: 50,
        tagPadX: 26,
        tagGap: 16,
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
        const card = this.getCardRect();

        this.drawBackground(ctx);
        this.drawCardFrame(ctx, card);
        this.drawCardPhoto(ctx, heroImage, card);
        this.drawPhotoFade(ctx, card);
        this.drawBrand(ctx, card);
        this.drawContent(ctx, data, card);
        this.drawFooter(ctx, data, card);

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

    getCardRect() {
        const footerReserve =
            this.LAYOUT.cardFooterGap + this.LAYOUT.footerBlockHeight + this.LAYOUT.footerBottomPad;
        return {
            x: this.LAYOUT.cardMarginX,
            y: this.LAYOUT.cardMarginTop,
            w: this.WIDTH - this.LAYOUT.cardMarginX * 2,
            h: this.HEIGHT - this.LAYOUT.cardMarginTop - footerReserve,
        };
    },

    getCardInner(card) {
        const b = this.LAYOUT.cardBorder;
        return {
            x: card.x + b,
            y: card.y + b,
            w: card.w - b * 2,
            h: card.h - b * 2,
        };
    },

    getFooterTop(card) {
        return card.y + card.h + this.LAYOUT.cardFooterGap;
    },

    drawBackground(ctx) {
        ctx.fillStyle = this.COLORS.canvas;
        ctx.fillRect(0, 0, this.WIDTH, this.HEIGHT);
    },

    drawCardFrame(ctx, card) {
        ctx.save();
        ctx.shadowColor = "rgba(0, 0, 0, 0.45)";
        ctx.shadowBlur = 48;
        ctx.shadowOffsetY = 12;
        ctx.fillStyle = this.COLORS.cardBorder;
        this.roundRect(ctx, card.x, card.y, card.w, card.h, 8);
        ctx.fill();
        ctx.restore();

        const inner = this.getCardInner(card);
        ctx.fillStyle = this.COLORS.cardInner;
        this.roundRect(ctx, inner.x, inner.y, inner.w, inner.h, 4);
        ctx.fill();
    },

    drawCardPhoto(ctx, img, card) {
        const inner = this.getCardInner(card);
        const photoH = Math.round(inner.h * this.LAYOUT.cardPhotoRatio);

        ctx.save();
        this.roundRect(ctx, inner.x, inner.y, inner.w, inner.h, 4);
        ctx.clip();
        this.drawCover(ctx, img, inner.x, inner.y, inner.w, photoH + this.LAYOUT.panelPhotoOverlap, 0.12);
        ctx.restore();
    },

    drawPhotoFade(ctx, card) {
        const inner = this.getCardInner(card);
        const photoH = Math.round(inner.h * this.LAYOUT.cardPhotoRatio);
        const fadeY = inner.y + photoH - this.LAYOUT.panelPhotoOverlap;

        const g = ctx.createLinearGradient(0, fadeY, 0, fadeY + this.LAYOUT.panelPhotoOverlap + 80);
        g.addColorStop(0, "rgba(18, 18, 24, 0)");
        g.addColorStop(0.55, "rgba(18, 18, 24, 0.55)");
        g.addColorStop(1, "rgba(18, 18, 24, 0.88)");
        ctx.fillStyle = g;
        ctx.fillRect(inner.x, fadeY, inner.w, inner.h - photoH + this.LAYOUT.panelPhotoOverlap + 80);
    },

    drawBrand(ctx, card) {
        const inner = this.getCardInner(card);
        ctx.textAlign = "left";
        ctx.textBaseline = "alphabetic";
        ctx.fillStyle = "rgba(255, 255, 255, 0.92)";
        ctx.font = this.font(700, this.TYPOGRAPHY.header);
        ctx.fillText(
            this.APP_NAME,
            inner.x + this.LAYOUT.logoInsetX,
            inner.y + this.LAYOUT.logoInsetY,
        );
    },

    font(weight, size) {
        return `${weight} ${size}px ${this.FONT}`;
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

    buildContentBlocks(ctx, data, maxWidth) {
        const subtitleFont = this.font(600, this.TYPOGRAPHY.subtitle);
        const titleFont = this.font(600, this.TYPOGRAPHY.title);
        const taglineFont = this.font(500, this.TYPOGRAPHY.tagline);
        const descFont = this.font(400, this.TYPOGRAPHY.desc);
        const tagFont = this.font(600, this.TYPOGRAPHY.tag);
        const tagHeight = this.LAYOUT.tagHeight;
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
                        const tw = metrics.width + this.LAYOUT.tagPadX * 2;
                        if (tagX + tw > x + maxWidth) return;

                        ctx.fillStyle = this.COLORS.tagFill;
                        ctx.strokeStyle = this.COLORS.tagBorder;
                        ctx.lineWidth = 2;
                        this.roundRect(ctx, tagX, topY, tw, tagHeight, 24);
                        ctx.fill();
                        ctx.stroke();

                        this.drawTextLine(
                            ctx,
                            tag,
                            tagX + this.LAYOUT.tagPadX,
                            topY + 8,
                            tagFont,
                            this.COLORS.white,
                        );
                        tagX += tw + this.LAYOUT.tagGap;
                    });
                },
            });
        }

        return blocks;
    },

    measureBlocks(blocks) {
        let totalHeight = 0;
        blocks.forEach((block) => {
            totalHeight += block.gapBefore + block.height;
        });
        return totalHeight;
    },

    drawContent(ctx, data, card) {
        const inner = this.getCardInner(card);
        const inset = this.LAYOUT.panelInset;
        const pad = this.LAYOUT.panelPad;
        const panelX = inner.x + inset;
        const panelW = inner.w - inset * 2;
        const maxWidth = panelW - pad * 2;
        const panelBottom = inner.y + inner.h - inset;

        const blocks = this.buildContentBlocks(ctx, data, maxWidth);
        const contentHeight = this.measureBlocks(blocks);
        const panelH = contentHeight + pad * 2;
        const photoH = Math.round(inner.h * this.LAYOUT.cardPhotoRatio);
        let panelY = inner.y + photoH - this.LAYOUT.panelPhotoOverlap;

        const minPanelY = inner.y + photoH - 120;
        if (panelY < minPanelY) panelY = minPanelY;
        if (panelY + panelH > panelBottom) {
            panelY = panelBottom - panelH;
        }

        ctx.save();
        this.roundRect(ctx, panelX, panelY, panelW, panelH, this.LAYOUT.panelRadius);
        ctx.fillStyle = this.COLORS.panelFill;
        ctx.fill();
        ctx.strokeStyle = this.COLORS.panelStroke;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.restore();

        let y = panelY + pad;
        blocks.forEach((block) => {
            y += block.gapBefore;
            block.draw(panelX + pad, y);
            y += block.height;
        });
    },

    drawFooter(ctx, data, card) {
        const pad = this.LAYOUT.cardMarginX;
        const centerX = this.WIDTH / 2;
        const bottomPad = this.LAYOUT.footerBottomPad;
        const footerTop = this.getFooterTop(card);

        ctx.strokeStyle = this.COLORS.divider;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(pad, footerTop);
        ctx.lineTo(this.WIDTH - pad, footerTop);
        ctx.stroke();

        ctx.textAlign = "center";
        ctx.textBaseline = "alphabetic";

        const brandY = footerTop + 38;
        ctx.fillStyle = this.COLORS.white;
        ctx.font = this.font(700, this.TYPOGRAPHY.footerBrand);
        ctx.fillText(this.APP_NAME, centerX, brandY);

        ctx.fillStyle = this.COLORS.footerLoc;
        ctx.font = this.font(500, this.TYPOGRAPHY.footerLoc);
        ctx.fillText(data.location, centerX, brandY + 32);

        ctx.fillStyle = this.COLORS.footerTags;
        ctx.font = this.font(600, this.TYPOGRAPHY.footerTags);
        ctx.fillText(data.hashtags, centerX, this.HEIGHT - bottomPad);
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
