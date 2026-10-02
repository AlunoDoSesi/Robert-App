document.addEventListener("DOMContentLoaded", () => {
    const imageInput = document.querySelector("[data-image-input]");
    const imagePreview = document.querySelector("[data-image-preview]");
    const uploadZone = document.querySelector(".upload-zone");

    if (imageInput && imagePreview) {
        imageInput.addEventListener("change", () => {
            const [file] = imageInput.files;
            if (!file) {
                imagePreview.removeAttribute("src");
                imagePreview.classList.remove("is-visible");
                return;
            }
            imagePreview.src = URL.createObjectURL(file);
            imagePreview.classList.add("is-visible");
        });

        ["dragenter", "dragover"].forEach((eventName) => {
            uploadZone?.addEventListener(eventName, (event) => {
                event.preventDefault();
                uploadZone.classList.add("is-dragging");
            });
        });
        ["dragleave", "drop"].forEach((eventName) => {
            uploadZone?.addEventListener(eventName, (event) => {
                event.preventDefault();
                uploadZone.classList.remove("is-dragging");
            });
        });
        uploadZone?.addEventListener("drop", (event) => {
            const [file] = event.dataTransfer.files;
            if (!file || !file.type.startsWith("image/")) return;
            const transfer = new DataTransfer();
            transfer.items.add(file);
            imageInput.files = transfer.files;
            imageInput.dispatchEvent(new Event("change"));
        });
    }

    document.querySelectorAll(".type-option input").forEach((input) => {
        input.addEventListener("change", () => {
            document.querySelectorAll(".type-option").forEach((option) => option.classList.remove("is-selected"));
            input.closest(".type-option")?.classList.add("is-selected");
        });
    });

    document.querySelectorAll(".flash-close").forEach((button) => {
        button.addEventListener("click", () => button.closest(".flash")?.remove());
    });

    window.setTimeout(() => {
        document.querySelectorAll(".flash").forEach((flash) => {
            flash.style.opacity = "0";
            flash.style.transform = "translateY(-5px)";
            window.setTimeout(() => flash.remove(), 220);
        });
    }, 6500);

    document.querySelectorAll(".item-form").forEach((form) => {
        form.addEventListener("submit", () => {
            const submit = form.querySelector("button[type='submit']");
            if (!submit) return;
            submit.disabled = true;
            submit.style.opacity = ".75";
            submit.innerHTML = "Publicando...";
        });
    });
});
