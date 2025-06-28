// Assests import
import YtLogo from "../../assets/yt.svg";

// types import
import type { SongCardProps } from "../../types";

function SongCard({ fetchedSong }: SongCardProps) {
    // check if fetchedSong is null or undefined
    if (!fetchedSong) {
        return <> </>;
    }

    return (
        <>
            {fetchedSong.map((fetchedSong, idx) => {
                return (
                    <div
                        key={idx}
                        className="card lg:card-side bg-whiteCard text-black shadow-sm w-[97%] font-family-jeju"
                    >
                        <figure>
                            <img
                                src={fetchedSong.thumbnail}
                                alt="Album"
                                className="aspect-video"
                            />
                        </figure>
                        <div className="card-body">
                            <h2 className="card-title truncate">
                                {fetchedSong.title}
                            </h2>
                            <p className="-mt-2 text-base">
                                {fetchedSong.artist}
                            </p>
                            {fetchedSong.timestamp && (
                                <p className="-mt-2 text-base">
                                    Timestamp: {fetchedSong.timestamp.toFixed()}{" "}
                                    seconds
                                </p>
                            )}
                            <div className="card-actions justify-end">
                                <a
                                    href={`https://www.youtube.com/watch?v=${fetchedSong.yt_url}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    <button className="px-4 py-2 rounded-lg bg-ytRed cursor-pointer">
                                        <img src={YtLogo} alt="Yt Logo" />
                                    </button>
                                </a>
                            </div>
                        </div>
                    </div>
                );
            })}
        </>
    );
}

export default SongCard;
