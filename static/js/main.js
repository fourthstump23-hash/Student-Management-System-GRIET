/**
 * GRIET Student Management System - Client Scripts
 * Provides live table search, modal interactions, SQL query copy,
 * and auto grade suggestion.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Initialize table search on any page with a .search-input
  const searchInputs = document.querySelectorAll(".search-input");
  searchInputs.forEach(input => {
    const tableId = input.getAttribute("data-table");
    if (tableId) {
      initTableSearch(input, document.getElementById(tableId));
    }
  });

  // Auto calculate grade based on marks
  const marksInput = document.getElementById("marks-input");
  const gradeSelect = document.getElementById("grade-select");
  if (marksInput && gradeSelect) {
    marksInput.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      if (!isNaN(val)) {
        if (val >= 90) gradeSelect.value = "A";
        else if (val >= 80) gradeSelect.value = "B";
        else if (val >= 70) gradeSelect.value = "C";
        else if (val >= 60) gradeSelect.value = "D";
        else gradeSelect.value = "F";
      }
    });
  }

  // Flash message dismissal
  document.querySelectorAll(".alert-close").forEach(btn => {
    btn.addEventListener("click", () => {
      const alert = btn.closest(".alert");
      if (alert) {
        alert.style.transition = "opacity 0.3s ease";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 300);
      }
    });
  });
});

/**
 * Universal table search filter
 */
function initTableSearch(inputEl, tableEl) {
  if (!inputEl || !tableEl) return;
  const tbody = tableEl.querySelector("tbody");
  if (!tbody) return;

  const rows = tbody.querySelectorAll("tr:not(.no-results-row)");
  const countBadge = document.getElementById(inputEl.getAttribute("data-count-target"));

  inputEl.addEventListener("input", () => {
    const query = inputEl.value.trim().toLowerCase();
    let visibleCount = 0;

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      const match = text.includes(query);
      row.style.display = match ? "" : "none";
      if (match) visibleCount++;
    });

    // Check or create no-results placeholder
    let noResultsRow = tbody.querySelector(".no-results-row");
    if (visibleCount === 0 && rows.length > 0) {
      if (!noResultsRow) {
        noResultsRow = document.createElement("tr");
        noResultsRow.className = "no-results-row";
        const colSpan = tableEl.querySelectorAll("thead th").length || 6;
        noResultsRow.innerHTML = `
          <td colspan="${colSpan}" style="text-align: center; padding: 28px; color: #94a3b8; font-weight: 500;">
            🔍 No matching records found for "<strong>${escapeHtml(query)}</strong>"
          </td>
        `;
        tbody.appendChild(noResultsRow);
      } else {
        noResultsRow.style.display = "";
        const querySpan = noResultsRow.querySelector("strong");
        if (querySpan) querySpan.textContent = query;
      }
    } else if (noResultsRow) {
      noResultsRow.style.display = "none";
    }

    if (countBadge) {
      countBadge.textContent = `${visibleCount} record${visibleCount === 1 ? '' : 's'}`;
    }
  });
}

/**
 * Copy SQL query from code box
 */
function copySQL(buttonEl) {
  const container = buttonEl.closest(".sql-box");
  if (!container) return;
  const pre = container.querySelector("pre");
  if (!pre) return;

  const text = pre.innerText;
  navigator.clipboard.writeText(text).then(() => {
    const originalText = buttonEl.innerHTML;
    buttonEl.innerHTML = "✓ Copied!";
    buttonEl.style.backgroundColor = "rgba(16, 185, 129, 0.4)";
    buttonEl.style.color = "#ffffff";
    setTimeout(() => {
      buttonEl.innerHTML = originalText;
      buttonEl.style.backgroundColor = "";
      buttonEl.style.color = "";
    }, 2000);
  }).catch(err => {
    console.error("Failed to copy:", err);
  });
}

/**
 * Modal utilities
 */
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.add("active");
    // Auto focus first input
    const firstInput = modal.querySelector("input:not([type=hidden]), select");
    if (firstInput) firstInput.focus();
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove("active");
  }
}

// Close modals when clicking on backdrop
window.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-backdrop")) {
    e.target.classList.remove("active");
  }
});

// Escape HTML helper
function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
