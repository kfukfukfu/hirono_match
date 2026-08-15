/**
 * result-share.js — 画面上の result-story-card をそのままキャプチャして共有画像化
 */

const ResultShare = {
    STORY_WIDTH: 1080,
    STORY_HEIGHT: 1920,

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
                const canvas = await this.generate();
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

    async generate() {
        const card = document.getElementById("result-card");
        if (!card) {
            throw new Error("result card not found");
        }
        if (typeof html2canvas !== "function") {
            throw new Error("html2canvas not loaded");
        }

        await this.waitForImages(card);

        const width = card.getBoundingClientRect().width;
        if (!width) {
            throw new Error("result card has no width");
        }

        const scale = this.STORY_WIDTH / width;
        const captured = await html2canvas(card, {
            scale,
            useCORS: true,
            backgroundColor: null,
            logging: false,
        });

        return this.fitToStory(captured);
    },

    waitForImages(root) {
        const images = [...root.querySelectorAll("img")];
        return Promise.all(
            images.map(
                (img) =>
                    new Promise((resolve) => {
                        if (img.complete) {
                            resolve();
                            return;
                        }
                        img.addEventListener("load", resolve, { once: true });
                        img.addEventListener("error", resolve, { once: true });
                    }),
            ),
        );
    },

    fitToStory(source) {
        const canvas = document.createElement("canvas");
        canvas.width = this.STORY_WIDTH;
        canvas.height = this.STORY_HEIGHT;
        const ctx = canvas.getContext("2d");

        const srcRatio = source.width / source.height;
        const dstRatio = this.STORY_WIDTH / this.STORY_HEIGHT;
        let drawWidth;
        let drawHeight;
        let offsetX;
        let offsetY;

        if (srcRatio > dstRatio) {
            drawHeight = this.STORY_HEIGHT;
            drawWidth = this.STORY_HEIGHT * srcRatio;
            offsetX = (this.STORY_WIDTH - drawWidth) / 2;
            offsetY = 0;
        } else {
            drawWidth = this.STORY_WIDTH;
            drawHeight = this.STORY_WIDTH / srcRatio;
            offsetX = 0;
            offsetY = (this.STORY_HEIGHT - drawHeight) / 2;
        }

        ctx.fillStyle = "#f0f7fa";
        ctx.fillRect(0, 0, this.STORY_WIDTH, this.STORY_HEIGHT);
        ctx.drawImage(source, offsetX, offsetY, drawWidth, drawHeight);

        return canvas;
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
