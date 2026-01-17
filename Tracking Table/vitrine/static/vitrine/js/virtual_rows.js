

function syncFrameHeights() {
    const all_frame_sizes = document.querySelectorAll('[id^="frame-size-"]');

    for (let i = 0; i < all_frame_sizes.length; i++) {

        const frame_size = all_frame_sizes[i];
        const frame_size_id = frame_size.id.replace('frame-size-', '');
        const frame_size_height = frame_size.offsetHeight;

        const frame_color = document.getElementById('frame-color-' + frame_size_id);
        const frame_glass = document.getElementById('frame-glass-' + frame_size_id);

        if (frame_color) {
            frame_color.style.height = frame_size_height + 'px';
            frame_color.style.display = 'flex';
            frame_color.style.alignItems = 'center';
        }

        if (frame_glass) {
            frame_glass.style.height = frame_size_height + 'px';
            frame_glass.style.display = 'flex';
            frame_glass.style.alignItems = 'center';
        }

    }

}

syncFrameHeights();
