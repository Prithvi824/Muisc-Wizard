// libraries import
import { useEffect, useState } from "react";

// components import
import Nav from "../common/nav";
import SongCard from "../common/songCard";

// Importing environment variables
const API_URL = import.meta.env.VITE_API_URL;

// import types
import type {
    GetAudioResponse,
    AddAudioResponse,
    ApiResponse,
} from "../../types";

function Song() {
    // set state to hold songs
    const [songs, setSongs] = useState<AddAudioResponse[]>([]);

    async function fetchSongs(): Promise<GetAudioResponse | null> {
        try {
            // add params
            const params = new URLSearchParams({
                limit: "100",
            });

            // create url
            const fullUrl = `${API_URL}/songs?${params.toString()}`;

            // Fetch the songs from the API
            const response = await fetch(fullUrl);
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            // Parse the JSON response
            let jsonData: ApiResponse<GetAudioResponse> = await response.json();
            let data = jsonData.data;
            return data as GetAudioResponse;
        } catch (error) {
            console.error("Failed to fetch songs:", error);
            return null;
        }
    }

    useEffect(() => {
        // Fetch songs when the component mounts
        fetchSongs().then((data) => {
            // Check if data is available
            if (data && data.songs) {
                setSongs(data.songs);
            }
        });
    }, []);

    return (
        <>
            <div className="bg-[#A6AEBF] w-full h-16 rounded-2xl relative text-black">
                <Nav />
            </div>
            <div className="p-2 flex flex-col items-center justify-center gap-4 mt-4 ">
                {songs.length === 0 ? (
                    <p>No songs found.</p>
                ) : (
                    <SongCard fetchedSong={songs} />
                )}
            </div>
        </>
    );
}

export default Song;
