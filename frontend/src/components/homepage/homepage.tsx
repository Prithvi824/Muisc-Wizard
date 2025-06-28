// Import necessary libraries
import { useState } from "react";

// components import
import Hero from "./hero";
import SongCard from "../common/songCard";
import InputDiv from "../common/inputDiv";

// types import
import type { AudioMatch } from "../../types";

function Homepage() {
    // State to hold the fetched song data
    const [fetchedSong, setFetchedSong] = useState<Array<AudioMatch> | null>(null);

    return (
        <main className="flex flex-col items-center justify-center gap-6 relative min-h-svh">
            <Hero setFetchedSong={setFetchedSong} />
            <SongCard fetchedSong={fetchedSong} />
            <InputDiv />
            <div className="flex-grow"></div>
            <footer className="flex flex-col items-center justify-center w-full pb-4">
                <span className="text-sm text-gray-500">
                    Thank You for stopping by!!
                </span>
                <span className="text-sm text-gray-500">
                    Created by Prithvi Srivastava
                </span>
            </footer>
        </main>
    );
}

export default Homepage;
