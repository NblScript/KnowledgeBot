// KnowledgeBot Documentation Extra JavaScript

// Add copy button to code blocks
document.addEventListener("DOMContentLoaded", function() {
  // Add copy button functionality is handled by Material theme
  
  // Add external link indicator
  document.querySelectorAll('a[href^="http"]').forEach(link => {
    if (!link.hostname.includes('knowledgebot.io') && !link.hostname.includes('github.com')) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
    }
  });
  
  // Add permalink hover effect
  document.querySelectorAll('.headerlink').forEach(link => {
    link.addEventListener('mouseenter', function() {
      this.style.opacity = '1';
    });
    link.addEventListener('mouseleave', function() {
      this.style.opacity = '0';
    });
  });
  
  // Add table sort functionality
  document.querySelectorAll('table').forEach(table => {
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
      header.style.cursor = 'pointer';
      header.addEventListener('click', () => {
        sortTable(table, index);
      });
    });
  });
  
  // Add scroll progress indicator
  const progressBar = document.createElement('div');
  progressBar.id = 'scroll-progress';
  progressBar.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    background: linear-gradient(90deg, #4F46E5, #818CF8);
    width: 0%;
    z-index: 1000;
    transition: width 0.1s ease;
  `;
  document.body.appendChild(progressBar);
  
  window.addEventListener('scroll', () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = (scrollTop / docHeight) * 100;
    progressBar.style.width = scrollPercent + '%';
  });
});

// Table sort function
function sortTable(table, columnIndex) {
  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const isNumeric = rows.every(row => {
    const cell = row.querySelectorAll('td')[columnIndex];
    return cell && !isNaN(parseFloat(cell.textContent));
  });
  
  const sortedRows = rows.sort((a, b) => {
    const aCell = a.querySelectorAll('td')[columnIndex];
    const bCell = b.querySelectorAll('td')[columnIndex];
    
    if (!aCell || !bCell) return 0;
    
    const aValue = aCell.textContent.trim();
    const bValue = bCell.textContent.trim();
    
    if (isNumeric) {
      return parseFloat(aValue) - parseFloat(bValue);
    }
    
    return aValue.localeCompare(bValue);
  });
  
  // Toggle sort direction
  if (table.dataset.sortColumn == columnIndex && table.dataset.sortDirection == 'asc') {
    sortedRows.reverse();
    table.dataset.sortDirection = 'desc';
  } else {
    table.dataset.sortDirection = 'asc';
  }
  table.dataset.sortColumn = columnIndex;
  
  // Re-add rows to tbody
  sortedRows.forEach(row => tbody.appendChild(row));
}

// Mermaid diagram initialization
if (typeof mermaid !== 'undefined') {
  mermaid.initialize({
    startOnLoad: true,
    theme: document.querySelector('[data-md-color-scheme]')?.getAttribute('data-md-color-scheme') === 'slate' ? 'dark' : 'default',
    securityLevel: 'loose'
  });
}