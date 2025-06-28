// Import libraries
import { useCallback, useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';

// Importing environment variables
const API_URL = import.meta.env.VITE_API_URL;

interface PopupState {
  visible: boolean;
  message: string;
}

function Layout() {
  const [popup, setPopup] = useState<PopupState>({ visible: false, message: '' });

  // Example: show a demo message on first mount. Replace or remove this according to your app logic.
  useEffect(() => {
    // Comment out the next line after integrating real trigger logic.
    setPopup({ visible: true, message: `Please note: The Wizard may struggle with noise or low volume but works well if clean clips of known songs are fed directly. You can do that through: ${API_URL}/docs` });
  }, []);

  const closePopup = useCallback(() => setPopup(prev => ({ ...prev, visible: false })), []);

  return (
    <section className="relative bg-linear-to-tr from-paleBlue-gradient-l to-paleBlue-gradient-r p-4 min-h-svh">
      {/* Child routes */}
      <Outlet />

      {/* Response Popup */}
      {popup.visible && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" aria-modal="true" role="dialog">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/50" onClick={closePopup}></div>

          {/* Popup container */}
          <div
            className="relative z-10 w-full max-w-md rounded-lg bg-white p-6 shadow-lg"
            onClick={e => e.stopPropagation()} // Prevent closing when clicking inside
          >
            {/* Close button */}
            <button
              type="button"
              className="absolute right-3 top-3 text-2xl font-semibold leading-none text-gray-500 hover:text-gray-700 focus:outline-none"
              aria-label="Close popup"
              onClick={closePopup}
            >
              &times;
            </button>

            {/* Message */}
            <p className="text-gray-800">{popup.message}</p>
          </div>
        </div>
      )}
    </section>
  );
}

export default Layout