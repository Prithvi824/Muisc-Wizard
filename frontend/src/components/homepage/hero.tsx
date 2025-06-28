// libraries import
import SiriWave from "siriwave";
import RecordRTC from "recordrtc";
import { useEffect, useRef, useState } from "react";

// assests import
import Nav from "../common/nav";
import Alert from "../common/alert";
import Microphone from "../common/microphone";

// Importing environment variables
const API_URL = import.meta.env.VITE_API_URL;

// Types import
import type { ApiResponse, AudioMatch, HeroProps, MicState } from "../../types";
import { MicStates } from "../../types";

function Hero({ setFetchedSong }: HeroProps) {
    // Refrences to DOM elements
    const siriContainerRef = useRef<HTMLDivElement | null>(null);
    const parentContainerRef = useRef<HTMLDivElement | null>(null);

    // Refrences to audio context and streams
    const streamRef = useRef<MediaStream | null>(null);
    const recorderRef = useRef<RecordRTC | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const audioAnalyzerRef = useRef<AnalyserNode | null>(null);
    const siriWaveRef = useRef<SiriWave | null>(null);
    const siriWaveDataRef = useRef<Uint8Array<ArrayBufferLike> | null>(null);

    // states
    const [isRecording, setIsRecording] = useState<Boolean>(false);
    const [micState, setMicState] = useState<MicState>(MicStates.Idle);
    const [alertMessage, setAlertMessage] = useState<string | null>("");

    function handleAlert(message: string) {
        // Set the alert message
        setAlertMessage(message);

        // Clear the alert message after 3 seconds
        setTimeout(() => {
            setAlertMessage(null);
        }, 3000);
    }

    useEffect(() => {
        // Ensure the container is available before initializing SiriWave
        if (!siriContainerRef.current) return;
        if (!parentContainerRef.current) return;

        // Initialize SiriWave after the component mounts
        const siriWave = new SiriWave({
            container: siriContainerRef.current,
            style: "ios9",
            cover: true,
        });

        // Set the SiriWave instance to state
        siriWaveRef.current = siriWave;

        // Cleanup on unmount
        return () => {
            siriWave.dispose();
        };
    }, []);

    // handle siri wave animation on state change
    useEffect(() => {
        // return if siriWaveRef is not initialized
        if (!siriWaveRef.current) return;

        if (isRecording) {
            // Start the SiriWave animation
            siriWaveRef.current.start();
            setMicState(MicStates.Recording);
        } else {
            // Stop the SiriWave animation
            siriWaveRef.current.stop();
        }
    }, [isRecording]);

    useEffect(() => {
        // If micState is Processing, animate the SiriWave
        if (micState === MicStates.Error) {
            // wait for 5 seconds before returning to idle state
            setTimeout(() => {
                setMicState(MicStates.Idle);
            }, 5000);
        }
    }, [micState]);

    function animateSiriWave() {
        // return if any condition is not met
        if (!siriWaveRef.current) return;
        if (!siriWaveDataRef.current) return;
        if (!audioAnalyzerRef.current) return;

        // call the animate function recursively
        requestAnimationFrame(animateSiriWave);

        // get the audio analyser and data array
        audioAnalyzerRef.current.getByteTimeDomainData(siriWaveDataRef.current);

        // the audio is silent at 128 so find the absolute difference from 128 and sum it up
        const sum = siriWaveDataRef.current.reduce(
            (acc, val) => acc + Math.abs(val - 128),
            0
        );

        // calculate the average amplitude
        const avg = sum / siriWaveDataRef.current.length;

        // set the amplitude of the SiriWave instance
        siriWaveRef.current.amplitude = Math.min(avg, 8); // Limit the amplitude to a maximum value
    }

    const startRecording = async () => {
        // get the user media stream
        streamRef.current = await navigator.mediaDevices.getUserMedia({
            audio: true,
        });

        // start recording the audio in wav format
        recorderRef.current = new RecordRTC(streamRef.current, {
            type: "audio",
            mimeType: "audio/wav",
            recorderType: RecordRTC.StereoAudioRecorder,
            disableLogs: true,
            sampleRate: 44100,
        });
        recorderRef.current.startRecording();

        // create an audio context and analyser
        audioContextRef.current = new AudioContext();
        audioAnalyzerRef.current = audioContextRef.current.createAnalyser();

        // set the audio source and connect it to the analyser
        const audioSource = audioContextRef.current.createMediaStreamSource(
            streamRef.current
        );
        audioSource.connect(audioAnalyzerRef.current);

        // bufferlength is the size of the array that will hold the audio data for animation of siri wave
        siriWaveDataRef.current = new Uint8Array(
            audioAnalyzerRef.current.frequencyBinCount
        );

        // At the end of startRecording
        animateSiriWave();

        // Set the SiriWave state to running
        setIsRecording(true);
    };

    const stopRecording = () => {
        // change the state to not recording
        setIsRecording(false);
        setMicState(MicStates.Processing);

        // get the audio blob from the recorder and upload it
        recorderRef.current?.stopRecording(async () => {
            // get the audio blob
            const audioBlob = recorderRef.current?.getBlob();
            if (!audioBlob) return;

            const audio = new Audio();
            audio.src = URL.createObjectURL(audioBlob);

            audio.onloadedmetadata = function () {
                // if the song duration is less than 15 second, show an error
                if (audio.duration < 15) {
                    handleAlert(
                        "Audio is too short. Please record for atleast 10 seconds."
                    );
                    setMicState(MicStates.Error);
                    return;
                }

                // upload the audio blob
                uploadAudio(audioBlob);
            };
        });

        // Stop all tracks
        streamRef.current?.getTracks().forEach((track) => track.stop());

        // Clean up Web Audio API nodes
        audioAnalyzerRef.current?.disconnect();
        audioContextRef.current?.close();

        // Reset references
        streamRef.current = null;
        audioAnalyzerRef.current = null;
        siriWaveDataRef.current = null;
        audioContextRef.current = null;
    };

    const uploadAudio = async (audioBlob: Blob) => {
        // check if the audio blob is valid
        if (!audioBlob || audioBlob.size === 0) {
            setMicState(MicStates.Error);
            return;
        }

        // Create a FormData object to send the audio file
        const formData = new FormData();
        formData.append("file", audioBlob, "recording.webm");

        try {
            // fetch the response
            const response = await fetch(`${API_URL}/match-audio`, {
                method: "POST",
                body: formData,
            });

            // Check if the response is ok
            if (!response.ok) {
                // create a empty object to set the fetched song to null
                const emptySong: AudioMatch[] = [
                    {
                        title: "Failed to fetch song",
                        yt_url: "Null",
                        thumbnail:
                            "https://img.freepik.com/free-vector/404-error-isometric-illustration_23-2148509538.jpg",
                        artist: "Null",
                        timestamp: 0,
                    },
                ];

                // Set the fetched song state to empty object
                setFetchedSong(emptySong);
            }

            // if no match is found
            if (response.status === 204) {
                // create a empty object to set the fetched song to null
                const emptySong: AudioMatch[] = [
                    {
                        title: "No match found",
                        yt_url: "Null",
                        thumbnail:
                            "https://img.freepik.com/free-vector/404-error-isometric-illustration_23-2148509538.jpg",
                        artist: "Null",
                        timestamp: 0,
                    },
                ];

                // Set the fetched song state to empty object
                setFetchedSong(emptySong);
            } else {
                // Parse the JSON response
                let responseData: ApiResponse<AudioMatch[]> = await response.json();

                // validate the response
                if (!responseData.data) return;

                // create a array with fetched songs
                const fetchedSongs: AudioMatch[] = responseData.data?.map((song) => {
                    return {
                        title: song.title,
                        yt_url: song.yt_url,
                        thumbnail:song.thumbnail,
                        artist: song.artist,
                        timestamp: song.timestamp,
                    }
                })

                // Set the fetched song state
                setFetchedSong(fetchedSongs);
            }
        } catch (error) {
            // reset the mic state to idle
            setMicState(MicStates.Error);
            console.error("Error uploading audio:", error);
        }

        // reset the mic state to idle
        setMicState(MicStates.Idle);
    };

    return (
        <>
            <div
                className="hero-container font-family-jeju relative h-64 w-full"
                ref={parentContainerRef}
            >
                <Nav />
                {alertMessage && <Alert text={alertMessage} />}
                <div ref={siriContainerRef} className="min-h-1/2"></div>
                <button
                    className="absolute right-4 bottom-4 bg-yellowOchar w-16 h-16 rounded-full flex justify-center items-center cursor-pointer"
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={micState === MicStates.Processing}
                >
                    <Microphone state={micState} />
                </button>
            </div>
        </>
    );
}

export default Hero;
