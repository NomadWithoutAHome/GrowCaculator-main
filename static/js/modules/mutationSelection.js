export function initializeMutationSearch() {
    const searchInput = document.getElementById('mutation-search');
    if (!searchInput) {
        console.warn('Mutation search input not found');
        return;
    }
    console.log('Initializing mutation search...');
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        console.log('Searching for mutations containing:', searchTerm);
        const mutationLabels = document.querySelectorAll('input[type="checkbox"][data-mutation]');
        let visibleCount = 0;
        mutationLabels.forEach(checkbox => {
            const label = checkbox.closest('label');
            if (!label) return;
            const mutationName = checkbox.dataset.mutation.toLowerCase();
            if (mutationName.includes(searchTerm)) {
                label.style.display = 'flex';
                visibleCount++;
            } else {
                label.style.display = 'none';
            }
        });
        console.log('Found', visibleCount, 'visible mutations');
    });
    searchInput.addEventListener('change', function() {
        if (this.value === '') {
            const mutationLabels = document.querySelectorAll('input[type="checkbox"][data-mutation]');
            mutationLabels.forEach(checkbox => {
                const label = checkbox.closest('label');
                if (label) label.style.display = 'flex';
            });
            console.log('Search cleared, showing all mutations');
        }
    });
    searchInput.addEventListener('keyup', function() {
        if (this.value === '') {
            const mutationLabels = document.querySelectorAll('input[type="checkbox"][data-mutation]');
            mutationLabels.forEach(checkbox => {
                const label = checkbox.closest('label');
                if (label) label.style.display = 'flex';
            });
        }
    });
    console.log('Mutation search functionality initialized successfully');
}

export function updateMutationDisplay(selectedMutations) {
    const mutationButtons = document.querySelectorAll('.mutation-chip');
    mutationButtons.forEach(button => {
        const mutation = button.getAttribute('data-mutation');
        if (selectedMutations.includes(mutation)) {
            button.classList.add('selected');
        } else {
            button.classList.remove('selected');
        }
    });
    const selectedDiv = document.getElementById('selected-mutations');
    const mutationList = document.getElementById('mutation-list');
    if (selectedDiv && mutationList) {
        if (selectedMutations.length > 0) {
            selectedDiv.classList.remove('hidden');
            mutationList.innerHTML = selectedMutations.map(mutation => 
                `<span class="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-sm">${mutation}</span>`
            ).join('');
        } else {
            selectedDiv.classList.add('hidden');
        }
    }
}
// Mutation selection and search logic
export function initializeMutationSelection() {
    const mutationCheckboxes = document.querySelectorAll('input[type="checkbox"][data-mutation]');
    const variantRadios = document.querySelectorAll('input[name="variant"]');
    
    console.log('Initializing mutation selection...');
    console.log('Found mutation checkboxes:', mutationCheckboxes.length);
    console.log('Found variant radios:', variantRadios.length);
    
    // Add scrollbar to mutations container if it exists
    const mutationsHeading = Array.from(document.querySelectorAll('h3')).find(h3 => 
        h3.textContent.includes('Environmental Mutations')
    );
    
    console.log('Found mutations heading:', mutationsHeading);
    
    if (mutationsHeading) {
        const mutationsContainer = mutationsHeading.closest('.bg-gray-800');
        console.log('Found mutations container:', mutationsContainer);
        
        if (mutationsContainer) {
            const mutationsGrid = mutationsContainer.querySelector('.grid');
            console.log('Found mutations grid:', mutationsGrid);
            
            if (mutationsGrid) {
                mutationsGrid.style.maxHeight = 'calc(6 * 2.5rem + 1rem)';
                mutationsGrid.style.overflowY = 'auto';
                mutationsGrid.style.scrollbarWidth = 'thin';
                mutationsGrid.style.scrollbarColor = '#10b981 #2d3748';
                mutationsGrid.style.setProperty('--scrollbar-thumb', '#10b981');
                mutationsGrid.style.setProperty('--scrollbar-track', '#2d3748');
                const existingStyle = document.getElementById('mutations-scrollbar-style');
                if (existingStyle) {
                    existingStyle.remove();
                }
                const style = document.createElement('style');
                style.id = 'mutations-scrollbar-style';
                style.textContent = `
                    .mutations-scrollable::-webkit-scrollbar {
                        width: 6px !important;
                        display: block !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-track {
                        background: #2d3748 !important;
                        border-radius: 3px !important;
                        display: block !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-thumb {
                        background: #10b981 !important;
                        border-radius: 3px !important;
                        min-height: 40px !important;
                        display: block !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-thumb:hover {
                        background: #059669 !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-button {
                        background: #10b981 !important;
                        height: 12px !important;
                        border-radius: 2px !important;
                        display: block !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-button:hover {
                        background: #059669 !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-button:single-button:start {
                        border-radius: 2px 2px 0 0 !important;
                    }
                    .mutations-scrollable::-webkit-scrollbar-button:single-button:end {
                        border-radius: 0 0 2px 2px !important;
                    }
                `;
                document.head.appendChild(style);
                mutationsGrid.classList.add('mutations-scrollable');
                mutationsGrid.offsetHeight;
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                            if (!mutationsGrid.style.overflowY || mutationsGrid.style.overflowY !== 'auto') {
                                mutationsGrid.style.maxHeight = 'calc(6 * 2.5rem + 1rem)';
                                mutationsGrid.style.overflowY = 'auto';
                                mutationsGrid.style.scrollbarWidth = 'thin';
                                mutationsGrid.style.scrollbarColor = '#10b981 #2d3748';
                            }
                        }
                    });
                });
                observer.observe(mutationsGrid, { attributes: true, attributeFilter: ['style'] });
                console.log('Scrollbar added to mutations grid with exact plant grid styling');
                console.log('Grid max height:', mutationsGrid.style.maxHeight);
                console.log('Grid overflow:', mutationsGrid.style.overflowY);
                console.log('Grid classes:', mutationsGrid.className);
                console.log('MutationObserver added to maintain scrollbar styling');
            } else {
                console.error('Mutations grid not found within container');
            }
        } else {
            console.error('Mutations container not found');
        }
    } else {
        console.error('Environmental Mutations heading not found');
    }
    
    // Initialize mutation search functionality
    console.log('About to initialize mutation search...');
    setTimeout(() => {
        if (window.initializeMutationSearch) {
            window.initializeMutationSearch();
        }
    }, 100);
    
    // Handle mutation checkboxes
    mutationCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const label = this.closest('label');
            // ...existing code for mutation checkbox change...
        });
    });
    // ...existing code for variant radios and other mutation selection logic...
}
