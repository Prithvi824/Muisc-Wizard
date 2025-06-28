// Import libraries
import { useState } from "react";
import type { ApiResponse, AddAudioResponse } from "../../types";

// Importing environment variables
const API_URL = import.meta.env.VITE_API_URL;

function InputDiv() {
    // State variables
    const [inputValue, setInputValue] = useState<string>("");
    const [hasError, setHasError] = useState<string | null>(null);
    const [videoDetails, setVideoDetails] = useState<AddAudioResponse | null>(
        null
    );
    const [isLoading, setIsLoading] = useState<boolean>(false);

    function triggerError(msg: string = "Failed to fetch video details.") {
        setHasError(msg);
        setTimeout(() => setHasError(null), 3000);
    }

    function validateUrl(url: string): boolean {
        // Regular expression to validate YouTube URL
        const youtubeUrlPattern =
            /^(?:https?:\/\/)?(?:www\.|m\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
        return youtubeUrlPattern.test(url);
    }

    async function submitVideoUrl(url: string) {
        // Validate the URL
        if (!validateUrl(url)) {
            triggerError("Invalid YouTube URL format.");
            return;
        }

        // create params
        const params = new URLSearchParams({
            yt_url: url,
        });

        // create the full URL with params
        const fullUrl = `${API_URL}/add-song?${params.toString()}`;

        // Fetch video details from the API
        let response = await fetch(fullUrl, { method: "GET" });
        setIsLoading(false);

        // Check if the response is ok
        if (!response.ok) {
            // If the response is not ok, set error state
            triggerError();
            return;
        }

        // Parse the response as JSON
        let apiData: ApiResponse<AddAudioResponse> = await response.json();

        // Check if the data is present
        if (!apiData.data) {
            triggerError();
            return;
        }

        // set the added video details
        setVideoDetails(apiData.data);
    }

    return (
        <div className="card lg:card-side bg-paleBlue-gradient-r text-black shadow-sm w-[97%] font-family-jeju">
            <div className="card-body">
                <h2 className="card-title truncate text-2xl">Add a Song</h2>

                {/* Show the thumbnail of the fetched video */}
                {videoDetails && (
                    <div className="text-start">
                        <img
                            src={videoDetails.thumbnail}
                            alt="Album"
                            className="aspect-video rounded-lg"
                        />
                        <h2 className="text-lg mt-2 truncate">
                            {videoDetails.title}
                        </h2>
                        <h3 className="text-green-900 -mt-1">
                            Song added to database.
                        </h3>
                    </div>
                )}

                {/* Input area */}
                <div className="mt-6">
                    <h2 className="text-xl mb-2">Enter the Youtube Link</h2>
                    <input
                        type="text"
                        value={inputValue}
                        placeholder="https://www.youtube.com/watch?v=AiZuT69qJLc"
                        className="bg-white pr-4 pl-2 py-2 w-full rounded-lg text-sm"
                        onChange={(e) => setInputValue(e.target.value)}
                    />
                    {hasError && (
                        <h1 className="text-red-700 text-base py-2">
                            {hasError}
                        </h1>
                    )}
                    <div className="flex items-center justify-start mt-4">
                        <button
                            className="mt-2 bg-paleBlue-gradient-l text-black px-8 py-2 rounded-lg text-base hover:cursor-pointer"
                            onClick={() => {
                                setInputValue(""); // Clear the input field
                            }}
                        >
                            Reset
                        </button>
                        <button
                            className="mt-2 ml-4 bg-greenBtn text-black px-8 py-2 rounded-lg text-base hover:cursor-pointer flex items-center justify-center"
                            onClick={() => {
                                setIsLoading(true);
                                submitVideoUrl(inputValue);
                            }}
                        >
                            {isLoading ? (
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 200 200"
                                    width="26"
                                    height="26"
                                    className="block"
                                >
                                    <circle
                                        fill="#000000"
                                        stroke="#000000"
                                        strokeWidth="15"
                                        r="15"
                                        cx="40"
                                        cy="65"
                                    >
                                        <animate
                                            attributeName="cy"
                                            calcMode="spline"
                                            dur="2s"
                                            values="65;135;65;"
                                            keySplines=".5 0 .5 1;.5 0 .5 1"
                                            repeatCount="indefinite"
                                            begin="-.4s"
                                        />
                                    </circle>
                                    <circle
                                        fill="#000000"
                                        stroke="#000000"
                                        strokeWidth="15"
                                        r="15"
                                        cx="100"
                                        cy="65"
                                    >
                                        <animate
                                            attributeName="cy"
                                            calcMode="spline"
                                            dur="2s"
                                            values="65;135;65;"
                                            keySplines=".5 0 .5 1;.5 0 .5 1"
                                            repeatCount="indefinite"
                                            begin="-.2s"
                                        />
                                    </circle>
                                    <circle
                                        fill="#000000"
                                        stroke="#000000"
                                        strokeWidth="15"
                                        r="15"
                                        cx="160"
                                        cy="65"
                                    >
                                        <animate
                                            attributeName="cy"
                                            calcMode="spline"
                                            dur="2s"
                                            values="65;135;65;"
                                            keySplines=".5 0 .5 1;.5 0 .5 1"
                                            repeatCount="indefinite"
                                            begin="0s"
                                        />
                                    </circle>
                                </svg>
                            ) : (
                                "Submit"
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default InputDiv;
