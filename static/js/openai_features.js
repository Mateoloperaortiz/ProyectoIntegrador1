/**
 * OpenAI Features - Additional functionality for OpenAI integrations
 * Handles file uploads, speech-to-text, and structured output features
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const fileUploadBtn = document.getElementById('fileUploadBtn');
    const microphoneBtn = document.getElementById('microphoneBtn');
    const structuredOutputBtn = document.getElementById('structuredOutputBtn');
    const uploadFileBtn = document.getElementById('uploadFileBtn');
    const fileUploadForm = document.getElementById('fileUploadForm');
    const fileUploadProgress = document.getElementById('fileUploadProgress');
    const fileUploadInput = document.getElementById('fileUploadInput');
    const fileUploadMessageId = document.getElementById('fileUploadMessageId');
    const fileUploadConversationId = document.getElementById('fileUploadConversationId');
    const startMicrophoneBtn = document.getElementById('startMicrophoneBtn');
    const stopMicrophoneBtn = document.getElementById('stopMicrophoneBtn');
    const resetMicrophoneBtn = document.getElementById('resetMicrophoneBtn');
    const sendMicrophoneTranscriptionBtn = document.getElementById('sendMicrophoneTranscriptionBtn');
    const transcriptionText = document.getElementById('transcriptionText');
    const editTranscriptionBtn = document.getElementById('editTranscriptionBtn');
    const useStructuredOutput = document.getElementById('useStructuredOutput');
    const jsonSchema = document.getElementById('jsonSchema');
    const saveStructuredOutputBtn = document.getElementById('saveStructuredOutputBtn');
    
    // Constants
    const conversationId = fileUploadConversationId ? fileUploadConversationId.value : null;
    
    // Initialize stored preferences
    function initPreferences() {
        // Load structured output preferences
        const useStructuredOutputSetting = localStorage.getItem('useStructuredOutput');
        if (useStructuredOutput && useStructuredOutputSetting) {
            useStructuredOutput.checked = useStructuredOutputSetting === 'true';
        }
        
        const savedSchema = localStorage.getItem('jsonSchema');
        if (jsonSchema && savedSchema) {
            jsonSchema.value = savedSchema;
        }
    }
    
    // File Upload Modal
    if (fileUploadBtn) {
        fileUploadBtn.addEventListener('click', function() {
            const modal = new bootstrap.Modal(document.getElementById('fileUploadModal'));
            modal.show();
        });
    }
    
    // File Upload Handler
    if (uploadFileBtn && fileUploadForm) {
        uploadFileBtn.addEventListener('click', function() {
            if (!fileUploadInput.files[0]) {
                alert('Please select a file to upload');
                return;
            }
            
            const formData = new FormData(fileUploadForm);
            
            // Show progress
            fileUploadProgress.classList.remove('d-none');
            const progressBar = fileUploadProgress.querySelector('.progress-bar');
            progressBar.style.width = '0%';
            
            // Disable button during upload
            uploadFileBtn.disabled = true;
            uploadFileBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Uploading...';
            
            fetch('/openai_integration/api/files/upload/', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Upload failed');
                }
                return response.json();
            })
            .then(data => {
                console.log('File uploaded successfully:', data);
                
                // Store file ID in localStorage for this conversation
                const fileIds = JSON.parse(localStorage.getItem(`conversation_${conversationId}_fileIds`) || '[]');
                fileIds.push(data.file_id);
                localStorage.setItem(`conversation_${conversationId}_fileIds`, JSON.stringify(fileIds));
                
                // Reset form and hide modal
                fileUploadForm.reset();
                fileUploadProgress.classList.add('d-none');
                bootstrap.Modal.getInstance(document.getElementById('fileUploadModal')).hide();
                
                // Show success message
                const messageList = document.getElementById('message-list');
                const systemMessage = document.createElement('div');
                systemMessage.className = 'alert alert-success alert-dismissible fade show';
                systemMessage.innerHTML = `
                    <i class="fas fa-check-circle me-2"></i> 
                    File "${data.filename}" uploaded successfully and will be available in this conversation.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                messageList.appendChild(systemMessage);
                
                // Reset button
                uploadFileBtn.disabled = false;
                uploadFileBtn.innerHTML = '<i class="fas fa-upload me-2"></i> Upload';
            })
            .catch(error => {
                console.error('Error uploading file:', error);
                
                // Reset progress and show error
                fileUploadProgress.classList.add('d-none');
                alert('Error uploading file: ' + error.message);
                
                // Reset button
                uploadFileBtn.disabled = false;
                uploadFileBtn.innerHTML = '<i class="fas fa-upload me-2"></i> Upload';
            });
        });
    }
    
    // Structured Output Modal
    if (structuredOutputBtn) {
        structuredOutputBtn.addEventListener('click', function() {
            const modal = new bootstrap.Modal(document.getElementById('structuredOutputModal'));
            modal.show();
        });
    }
    
    // Save Structured Output Settings
    if (saveStructuredOutputBtn) {
        saveStructuredOutputBtn.addEventListener('click', function() {
            // Validate JSON schema if enabled
            if (useStructuredOutput.checked) {
                try {
                    // Validate that the schema is valid JSON
                    JSON.parse(jsonSchema.value);
                } catch (error) {
                    alert('Invalid JSON schema format. Please check your syntax.');
                    return;
                }
            }
            
            // Save preferences
            localStorage.setItem('useStructuredOutput', useStructuredOutput.checked);
            localStorage.setItem('jsonSchema', jsonSchema.value);
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('structuredOutputModal')).hide();
            
            // Show indicator if enabled
            if (useStructuredOutput.checked) {
                structuredOutputBtn.classList.add('text-success');
                structuredOutputBtn.innerHTML = '<i class="fas fa-code text-success"></i>';
            } else {
                structuredOutputBtn.classList.remove('text-success');
                structuredOutputBtn.innerHTML = '<i class="fas fa-code"></i>';
            }
        });
    }
    
    // Microphone Modal
    if (microphoneBtn) {
        microphoneBtn.addEventListener('click', function() {
            const modal = new bootstrap.Modal(document.getElementById('microphoneModal'));
            modal.show();
        });
    }
    
    // Speech-to-Text Functionality
    if (startMicrophoneBtn && stopMicrophoneBtn) {
        let mediaRecorder;
        let audioChunks = [];
        let recordingStartTime;
        let timerInterval;
        let audioBlob;
        
        // Start recording
        startMicrophoneBtn.addEventListener('click', function() {
            // Request microphone access
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    audioChunks = [];
                    mediaRecorder = new MediaRecorder(stream);
                    
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        // Stop timer
                        clearInterval(timerInterval);
                        
                        // Create blob from chunks and set to audio element
                        audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        document.getElementById('microphoneAudioPreview').src = audioUrl;
                        
                        // Show audio controls
                        document.getElementById('microphoneAudioControls').style.display = 'block';
                        document.getElementById('microphoneInstructions').innerText = 'Recording completed.';
                        document.getElementById('recordingTimerContainer').style.display = 'none';
                    };
                    
                    // Start recording
                    mediaRecorder.start();
                    
                    // Update UI
                    startMicrophoneBtn.style.display = 'none';
                    stopMicrophoneBtn.style.display = 'inline-block';
                    document.getElementById('microphoneInstructions').innerText = 'Recording in progress...';
                    document.getElementById('microphoneAudioControls').style.display = 'none';
                    document.getElementById('transcriptionContainer').style.display = 'none';
                    
                    // Start timer
                    recordingStartTime = Date.now();
                    document.getElementById('recordingTimerContainer').style.display = 'block';
                    updateMicrophoneTimer();
                    timerInterval = setInterval(updateMicrophoneTimer, 1000);
                })
                .catch(error => {
                    console.error('Error accessing microphone:', error);
                    document.getElementById('microphoneInstructions').innerText = 'Error: ' + error.message;
                    document.getElementById('microphoneInstructions').classList.add('text-danger');
                });
        });
        
        // Stop recording
        stopMicrophoneBtn.addEventListener('click', function() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                
                // Update UI
                startMicrophoneBtn.style.display = 'inline-block';
                stopMicrophoneBtn.style.display = 'none';
            }
        });
        
        // Reset recording
        if (resetMicrophoneBtn) {
            resetMicrophoneBtn.addEventListener('click', function() {
                document.getElementById('microphoneAudioControls').style.display = 'none';
                document.getElementById('microphoneInstructions').innerText = 'Click the microphone to start recording your message.';
                document.getElementById('microphoneAudioPreview').src = '';
                document.getElementById('transcriptionContainer').style.display = 'none';
                sendMicrophoneTranscriptionBtn.disabled = true;
                audioBlob = null;
            });
        }
        
        // Transcribe recording
        if (sendMicrophoneTranscriptionBtn) {
            document.getElementById('microphoneAudioPreview').addEventListener('play', function() {
                // Transcribe after first play
                if (!transcriptionText.value && audioBlob) {
                    transcribeAudio(audioBlob);
                }
            });
            
            // Send button action
            sendMicrophoneTranscriptionBtn.addEventListener('click', function() {
                if (transcriptionText.value) {
                    // Add text to message input and close modal
                    document.getElementById('id_content').value = transcriptionText.value;
                    bootstrap.Modal.getInstance(document.getElementById('microphoneModal')).hide();
                    
                    // Reset for next use
                    resetMicrophoneBtn.click();
                }
            });
            
            // Edit transcription button
            if (editTranscriptionBtn) {
                editTranscriptionBtn.addEventListener('click', function() {
                    // Make the transcription editable
                    transcriptionText.readOnly = false;
                    transcriptionText.focus();
                    
                    // Change button text
                    editTranscriptionBtn.innerHTML = '<i class="fas fa-check me-1"></i> Done';
                    
                    // Toggle button action
                    editTranscriptionBtn.removeEventListener('click', arguments.callee);
                    editTranscriptionBtn.addEventListener('click', function() {
                        transcriptionText.readOnly = true;
                        editTranscriptionBtn.innerHTML = '<i class="fas fa-edit me-1"></i> Edit';
                        
                        // Reset event listener
                        editTranscriptionBtn.removeEventListener('click', arguments.callee);
                        editTranscriptionBtn.addEventListener('click', arguments.callee.caller);
                    });
                });
            }
        }
        
        // Helper function to update timer display
        function updateMicrophoneTimer() {
            const elapsedMilliseconds = Date.now() - recordingStartTime;
            const elapsedSeconds = Math.floor(elapsedMilliseconds / 1000);
            const minutes = Math.floor(elapsedSeconds / 60);
            const seconds = elapsedSeconds % 60;
            
            document.getElementById('microphoneTimer').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // Function to transcribe audio
        function transcribeAudio(audioBlob) {
            // Show loading state in the transcription area
            document.getElementById('transcriptionContainer').style.display = 'block';
            transcriptionText.value = 'Transcribing...';
            transcriptionText.disabled = true;
            
            // Create form data with audio blob
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            
            // Add language if specified
            const language = document.getElementById('microphoneLanguage').value;
            if (language) {
                formData.append('language', language);
            }
            
            // Get CSRF token
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            
            // Send to server
            fetch('/openai_integration/api/stt/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Enable send button
                sendMicrophoneTranscriptionBtn.disabled = false;
                
                if (data.success) {
                    // Show transcription
                    transcriptionText.value = data.transcription;
                    transcriptionText.disabled = false;
                    transcriptionText.readOnly = true;
                } else {
                    // Show error
                    transcriptionText.value = 'Error: ' + data.error;
                    transcriptionText.disabled = false;
                    transcriptionText.readOnly = true;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                transcriptionText.value = 'Error transcribing audio: ' + error.message;
                transcriptionText.disabled = false;
                transcriptionText.readOnly = true;
            });
        }
    }
    
    // Initialize preferences
    initPreferences();
});
