/**
 * Helper functions for image understanding visualization
 */

function extractJSONFromText(text) {
    try {
        const jsonStart = text.indexOf('[') !== -1 ? text.indexOf('[') : text.indexOf('{');
        const jsonEnd = text.lastIndexOf(']') !== -1 ? text.lastIndexOf(']') + 1 : text.lastIndexOf('}') + 1;
        
        if (jsonStart !== -1 && jsonEnd !== -1) {
            const jsonText = text.substring(jsonStart, jsonEnd);
            return JSON.parse(jsonText);
        }
    } catch (e) {
        console.error("Error parsing JSON from text:", e);
    }
    return null;
}

function renderBoundingBoxes(imageUrl, boxesData) {
    const container = document.createElement('div');
    container.className = 'bounding-box-container';
    container.style.position = 'relative';
    container.style.display = 'inline-block';
    container.style.margin = '10px 0';
    
    const img = document.createElement('img');
    img.src = imageUrl;
    img.style.maxWidth = '100%';
    img.style.height = 'auto';
    container.appendChild(img);
    
    boxesData.forEach((box, index) => {
        if (box.box_2d && box.label) {
            const [yMin, xMin, yMax, xMax] = box.box_2d;
            
            const top = yMin / 10;
            const left = xMin / 10;
            const height = (yMax - yMin) / 10;
            const width = (xMax - xMin) / 10;
            
            const hue = (index * 137) % 360;
            const color = `hsl(${hue}, 100%, 50%)`;
            
            const boxElement = document.createElement('div');
            boxElement.className = 'bbox';
            boxElement.style.position = 'absolute';
            boxElement.style.top = `${top}%`;
            boxElement.style.left = `${left}%`;
            boxElement.style.width = `${width}%`;
            boxElement.style.height = `${height}%`;
            boxElement.style.border = `2px solid ${color}`;
            boxElement.style.backgroundColor = `${color}20`;
            boxElement.style.boxSizing = 'border-box';
            
            const label = document.createElement('span');
            label.textContent = box.label;
            label.style.position = 'absolute';
            label.style.top = '0';
            label.style.left = '0';
            label.style.backgroundColor = color;
            label.style.color = 'white';
            label.style.padding = '2px 4px';
            label.style.fontSize = '12px';
            label.style.borderRadius = '2px';
            
            boxElement.appendChild(label);
            container.appendChild(boxElement);
        }
    });
    
    return container;
}

function renderSegmentationMasks(imageUrl, segmentationData) {
    const container = document.createElement('div');
    container.className = 'segmentation-container';
    container.style.position = 'relative';
    container.style.display = 'inline-block';
    container.style.margin = '10px 0';
    
    const img = document.createElement('img');
    img.src = imageUrl;
    img.style.maxWidth = '100%';
    img.style.height = 'auto';
    container.appendChild(img);
    
    segmentationData.forEach((segment, index) => {
        if (segment.box_2d && segment.label && segment.mask) {
            const [yMin, xMin, yMax, xMax] = segment.box_2d;
            
            const top = yMin / 10;
            const left = xMin / 10;
            const height = (yMax - yMin) / 10;
            const width = (xMax - xMin) / 10;
            
            const hue = (index * 137) % 360;
            const color = `hsla(${hue}, 100%, 50%, 0.3)`;
            
            const segmentElement = document.createElement('div');
            segmentElement.className = 'segment';
            segmentElement.style.position = 'absolute';
            segmentElement.style.top = `${top}%`;
            segmentElement.style.left = `${left}%`;
            segmentElement.style.width = `${width}%`;
            segmentElement.style.height = `${height}%`;
            segmentElement.style.backgroundColor = color;
            segmentElement.style.backgroundImage = `url(data:image/png;base64,${segment.mask})`;
            segmentElement.style.backgroundSize = '100% 100%';
            segmentElement.style.backgroundBlendMode = 'multiply';
            segmentElement.style.boxSizing = 'border-box';
            
            const label = document.createElement('span');
            label.textContent = segment.label;
            label.style.position = 'absolute';
            label.style.top = '0';
            label.style.left = '0';
            label.style.backgroundColor = color.replace('0.3', '0.8');
            label.style.color = 'white';
            label.style.padding = '2px 4px';
            label.style.fontSize = '12px';
            label.style.borderRadius = '2px';
            
            segmentElement.appendChild(label);
            container.appendChild(segmentElement);
        }
    });
    
    return container;
}

document.addEventListener('DOMContentLoaded', function() {
    const messageList = document.getElementById('message-list');
    if (messageList) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.classList && node.classList.contains('message-bubble') && 
                            node.classList.contains('message-ai')) {
                            
                            const content = node.querySelector('.message-content');
                            if (content) {
                                const text = content.textContent;
                                
                                if (text.includes('box_2d') && !text.includes('mask')) {
                                    const boxesData = extractJSONFromText(text);
                                    if (boxesData && Array.isArray(boxesData)) {
                                        const prevUserMsg = node.previousElementSibling;
                                        if (prevUserMsg && prevUserMsg.classList.contains('message-user')) {
                                            const imgPreview = document.querySelector('.chat-image-preview img');
                                            if (imgPreview && imgPreview.src) {
                                                const boxesContainer = renderBoundingBoxes(imgPreview.src, boxesData);
                                                content.appendChild(boxesContainer);
                                            }
                                        }
                                    }
                                }
                                
                                if (text.includes('mask') && text.includes('box_2d')) {
                                    const segmentationData = extractJSONFromText(text);
                                    if (segmentationData && Array.isArray(segmentationData)) {
                                        const prevUserMsg = node.previousElementSibling;
                                        if (prevUserMsg && prevUserMsg.classList.contains('message-user')) {
                                            const imgPreview = document.querySelector('.chat-image-preview img');
                                            if (imgPreview && imgPreview.src) {
                                                const segmentContainer = renderSegmentationMasks(imgPreview.src, segmentationData);
                                                content.appendChild(segmentContainer);
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
            });
        });
        
        observer.observe(messageList, { childList: true });
    }
});
