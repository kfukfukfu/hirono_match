/**
 * script.js
 * ---------
 * お気に入り機能（localStorage）と共通 UI 操作を担当する JavaScript。
 */

const Favorites = {
    STORAGE_KEY: "hirono_match_favorites",

    getAll() {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || [];
        } catch {
            return [];
        }
    },

    save(list) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(list));
    },

    isFavorite(id) {
        return this.getAll().some((item) => String(item.id) === String(id));
    },

    add(spot) {
        const list = this.getAll();
        if (!this.isFavorite(spot.id)) {
            list.push(spot);
            this.save(list);
        }
    },

    remove(id) {
        const list = this.getAll().filter((item) => String(item.id) !== String(id));
        this.save(list);
    },

    toggle(spot) {
        if (this.isFavorite(spot.id)) {
            this.remove(spot.id);
            return false;
        }
        this.add(spot);
        return true;
    },

    renderList(listSelector, emptySelector) {
        const container = document.querySelector(listSelector);
        const emptyMsg = document.querySelector(emptySelector);
        if (!container) return;

        const list = this.getAll();
        container.innerHTML = "";

        if (list.length === 0) {
            if (emptyMsg) emptyMsg.hidden = false;
            return;
        }

        if (emptyMsg) emptyMsg.hidden = true;

        list.forEach((spot) => {
            const article = document.createElement("article");
            article.className = "spot-card";
            article.innerHTML = `
                <a href="/spot/${spot.id}">
                    <img src="/static/${spot.image}" alt="${spot.name}">
                    <div class="spot-card-body">
                        <span class="spot-category">${spot.category}</span>
                        <h3>${spot.name}</h3>
                    </div>
                </a>
                <button type="button" class="favorite-remove" data-spot-id="${spot.id}">
                    お気に入りから削除
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
        const card = btn.closest(".spot-card");
        const id = btn.dataset.spotId;

        if (Favorites.isFavorite(id)) {
            btn.textContent = "♥";
            btn.classList.add("is-favorite");
        }

        btn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();

            const img = card.querySelector("img");
            const name = card.querySelector("h3").textContent;
            const category = card.querySelector(".spot-category").textContent;

            const added = Favorites.toggle({
                id: id,
                name: name,
                image: img.getAttribute("src").replace("/static/", ""),
                category: category,
            });

            btn.textContent = added ? "♥" : "♡";
            btn.classList.toggle("is-favorite", added);
        });
    });
});
