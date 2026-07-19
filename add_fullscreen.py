import os

filepath = r"c:\Users\Vivek\Desktop\vpn sentinel\frontend\index.html"
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the Map Title to include a Fullscreen button
old_title = '<div class="chart-title" style="padding: 24px 24px 0 24px;">Global Threat Map</div>'
new_title = """<div class="chart-title" style="padding: 24px 24px 0 24px; display: flex; justify-content: space-between; align-items: center;">
                    Global Threat Map
                    <button onclick="toggleMapFullscreen()" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 500; transition: background 0.2s ease;">⛶ Fullscreen</button>
                </div>"""
html = html.replace(old_title, new_title)

# 2. Inject the JS function
js_function = """
        function toggleMapFullscreen() {
            const mapContainer = document.querySelector('.map-container');
            if (!document.fullscreenElement) {
                if (mapContainer.requestFullscreen) {
                    mapContainer.requestFullscreen();
                } else if (mapContainer.webkitRequestFullscreen) { /* Safari */
                    mapContainer.webkitRequestFullscreen();
                } else if (mapContainer.msRequestFullscreen) { /* IE11 */
                    mapContainer.msRequestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) { /* Safari */
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) { /* IE11 */
                    document.msExitFullscreen();
                }
            }
        }

        // Ensure Leaflet resizes correctly when entering/exiting fullscreen
        document.addEventListener('fullscreenchange', () => {
            if (threatMap) {
                setTimeout(() => {
                    threatMap.invalidateSize();
                }, 100);
            }
            
            const mapContainer = document.querySelector('.map-container');
            if (document.fullscreenElement) {
                mapContainer.style.background = '#020617'; // Set dark background in fullscreen
                mapContainer.style.padding = '20px';
                mapContainer.style.borderRadius = '0';
            } else {
                mapContainer.style.background = 'var(--panel-bg)';
                mapContainer.style.padding = '24px';
                mapContainer.style.borderRadius = '20px';
            }
        });

        window.onload = () => {"""

html = html.replace("        window.onload = () => {", js_function)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)
