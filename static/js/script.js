/**
 * script.js
 * ---------
 * お気に入り機能（localStorage）と共通 UI 操作を担当する JavaScript。
 * localStorage にはスポット ID のみ保存し、表示文言は API から取得する。
 */

const Favorites = {
    STORAGE_KEY: "hirono_match_favorites",

    getIds() {
        try {
            const raw = JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || [];
            if (raw.length > 0 && typeof raw[0] === "object") {
                const ids = raw.map((item) => String(item.id));
                this.saveIds(ids);
                return ids;
            }
            return raw.map(String);
        } catch {
            return [];
        }
    },

    saveIds(ids) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(ids.map(String)));
    },

    isFavorite(id) {
        return this.getIds().includes(String(id));
    },

    add(id) {
        const ids = this.getIds();
        const sid = String(id);
        if (!ids.includes(sid)) {
            ids.push(sid);
            this.saveIds(ids);
        }
    },

    remove(id) {
        this.saveIds(this.getIds().filter((item) => item !== String(id)));
    },

    toggle(id) {
        if (this.isFavorite(id)) {
            this.remove(id);
            return false;
        }
        this.add(id);
        return true;
    },

    async fetchSpots(ids) {
        if (ids.length === 0) return [];
        const res = await fetch(`/api/spots?ids=${ids.join(",")}`);
        if (!res.ok) return [];
        return res.json();
    },

    async renderList(listSelector, emptySelector) {
        const container = document.querySelector(listSelector);
        const emptyMsg = document.querySelector(emptySelector);
        if (!container) return;

        const ids = this.getIds();
        container.innerHTML = "";

        if (ids.length === 0) {
            if (emptyMsg) emptyMsg.hidden = false;
            return;
        }

        if (emptyMsg) emptyMsg.hidden = true;

        const spots = await this.fetchSpots(ids);
        const removeLabel =
            (window.HIRONO_I18N && window.HIRONO_I18N.favoritesRemove) ||
            "Remove from favorites";

        spots.forEach((spot) => {
            const article = document.createElement("article");
            article.className = "spot-card";
            article.innerHTML = `
                <a href="/spot/${spot.id}">
                    <img src="/static/${spot.image_url}" alt="${spot.name}">
                    <div class="spot-card-body">
                        <span class="spot-category">${spot.category}</span>
                        <h3>${spot.name}</h3>
                    </div>
                </a>
                <button type="button" class="favorite-remove" data-spot-id="${spot.id}">
                    ${removeLabel}
                </button>
            `;
            container.appendChild(article);
        });

        container.querySelectorAll(".favorite-remove").forEach((btn) => {
            btn.addEventListener("click", () => {
                Favorites.remove(btn.dataset.spotId);
                Favorites.renderList(listSelector, emptySelector);
            });
        });
    },
};

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".btn-favorite").forEach((btn) => {
        const id = btn.dataset.spotId;

        if (Favorites.isFavorite(id)) {
            btn.textContent = "♥";
            btn.classList.add("is-favorite");
        }

        btn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();

            const added = Favorites.toggle(id);
            btn.textContent = added ? "♥" : "♡";
            btn.classList.toggle("is-favorite", added);
        });
    });
});
