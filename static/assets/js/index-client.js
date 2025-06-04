
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const fileList = document.getElementById('file-list');
        const form = document.getElementById('upload-form');
        const progressBar = document.getElementById('upload-progress-bar');
        const progressBarInner = document.getElementById('progress-bar-inner');
    
        dropZone.addEventListener('dragover', e => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    
        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            fileInput.files = e.dataTransfer.files;
            displayFiles(fileInput.files);
        });
    
        fileInput.addEventListener('change', () => displayFiles(fileInput.files));
    
        function displayFiles(files) {
            fileList.innerHTML = '';  // Efface la liste existante
        
            for (let i = 0; i < files.length; i++) {
                const li = document.createElement('li');
                li.textContent = `${files[i].name} (${(files[i].size / 1024).toFixed(1)} Ko)`;
                fileList.appendChild(li);
            }
        }
        
    
        // Gestion du modal de suppression
        document.addEventListener('DOMContentLoaded', () => {
            $('#deleteModal').on('show.bs.modal', function (event) {
                const button = $(event.relatedTarget); // bouton qui a déclenché le modal
                
                const actionUrl = button.data('url');
               
                
                $(this).find('#delete-form').attr('action', actionUrl);
            });
        });
    