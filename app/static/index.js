window.addEventListener("DOMContentLoaded", main);

function main() {
    installIndexFormHandlers();
    installResponseHandlers();
}

function installIndexFormHandlers() {
    const formEl = document.querySelector(".js-index-url-form");
    if (!formEl) {
        return;
    }

    formEl.querySelectorAll("select").forEach((e) => {
        const choices = new Choices(e);
    });

    const enableForm = () => {
        formEl.querySelectorAll("input, select, button").forEach((e) => { 
            e.removeAttribute("disabled"); 
        });

        formEl.querySelectorAll(".js-index-url-form__text-default").forEach((e) => { 
            e.classList.remove("hidden");
        });

        formEl.querySelectorAll(".js-index-url-form__text-loading").forEach((e) => { 
            e.classList.add("hidden");
        });
    };

    const disableForm = () => {
        formEl.querySelectorAll("input, select, button").forEach((e) => { 
            e.setAttribute("disabled", "disabled"); 
        });

        formEl.querySelectorAll(".js-index-url-form__text-default").forEach((e) => { 
            e.classList.add("hidden");
        });

        formEl.querySelectorAll(".js-index-url-form__text-loading").forEach((e) => { 
            e.classList.remove("hidden");
        });
    };

    // const El = formEl.querySelector("input[name='url']");
    const buttonEl = formEl.querySelector("button");
    const selectEl = formEl.querySelector("select");
    const errorEl = document.querySelector(".error-data");

    formEl.addEventListener("submit", async (e) => {
        e.preventDefault();
        disableForm();

        errorEl.classList.add("hidden");

        const fd = new FormData(formEl);
        fd.append(selectEl.getAttribute("name"), selectEl.value);
        const response = await fetch(formEl.getAttribute("action"), {
            method: "POST",
            body: fd,
        });

        const data = await response.json();

        if (data.detail) {
            errorEl.classList.remove("hidden");
            errorEl.querySelector("div").innerText = JSON.stringify(data, undefined, 2)
        }

        renderResponse(data.data);

        enableForm();
    });
}

function renderResponse(data) {
    html = '';
    data.forEach((row) => {
        html += `
            <div class="response__item">
                <label class="response__item__title">
                    <input type="checkbox" class="js-response-item-selector" checked/>
                    <h3>${row.name}</h3>
                </label>
                <div class="response__item__textarea">
                    <button type="button" class="js-response-item-copy" title="Скопировать">📋</button>
                    <textarea>${row.payload_rendered}</textarea>
                </div>    
            </div>    
        `
    });
    document.querySelector(".js-response-app").innerHTML = html;
}

function installResponseHandlers() {
    document.addEventListener("change", (e) => {
        if (!e.target.closest(".response__item__title")) {
            return;
        }

        const wrapperEl = e.target.closest(".response__item");
        const checkboxEl = e.target;
        const textareaEl = wrapperEl.querySelector("textarea");
        if (checkboxEl.checked) {
            textareaEl.classList.remove("hidden");
        } else {
            textareaEl.classList.add("hidden");
        }
    });

    document.addEventListener("click", (e) => {
        if (!e.target.classList.contains("js-response-item-copy")) {
            return;
        }

        const wrapperEl = e.target.closest(".response__item");
        const textareaEl = wrapperEl.querySelector("textarea");
        navigator.clipboard.writeText(textareaEl.value);
    });
}