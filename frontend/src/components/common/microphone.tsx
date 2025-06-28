// import types
import { useEffect, useState } from "react";
import type { MicrophoneProps } from "../../types";
import { MicStates } from "../../types";

function Microphone({ state }: MicrophoneProps) {
    const [classValue, setClassValue] = useState<string>("");

    useEffect(() => {
        // Update classValue based on the state
        switch (state) {
            case MicStates.Idle:
                setClassValue("");
                break;
            case "RECORDING":
                setClassValue("animate-svg");
                break;
            case "PROCESSING":
                setClassValue("");
                break;
            default:
                setClassValue("");
        }
    }, [state]);

    if (state === MicStates.Processing) {
        return (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
                <rect
                    fill="#FF0000"
                    stroke="#FF0000"
                    strokeWidth="10"
                    strokeLinejoin="round"
                    width="30"
                    height="30"
                    x="85"
                    y="85"
                    rx="0"
                    ry="0"
                >
                    <animate
                        attributeName="rx"
                        calcMode="spline"
                        dur="1"
                        values="15;15;5;15;15"
                        keySplines=".5 0 .5 1;.8 0 1 .2;0 .8 .2 1;.5 0 .5 1"
                        repeatCount="indefinite"
                    ></animate>
                    <animate
                        attributeName="ry"
                        calcMode="spline"
                        dur="1.5"
                        values="15;15;10;15;15"
                        keySplines=".5 0 .5 1;.8 0 1 .2;0 .8 .2 1;.5 0 .5 1"
                        repeatCount="indefinite"
                    ></animate>
                    <animate
                        attributeName="height"
                        calcMode="spline"
                        dur="1.5"
                        values="30;30;1;30;30"
                        keySplines=".5 0 .5 1;.8 0 1 .2;0 .8 .2 1;.5 0 .5 1"
                        repeatCount="indefinite"
                    ></animate>
                    <animate
                        attributeName="y"
                        calcMode="spline"
                        dur="1.5"
                        values="40;170;40;"
                        keySplines=".6 0 1 .4;0 .8 .2 1"
                        repeatCount="indefinite"
                    ></animate>
                </rect>
            </svg>
        );
    } else if (state === MicStates.Error) {
        return (
            <svg
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
                className="w-8"
                fill="none"
            >
                <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
                <g
                    id="SVGRepo_tracerCarrier"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                ></g>
                <g id="SVGRepo_iconCarrier">
                    <path
                        d="M2.20164 18.4695L10.1643 4.00506C10.9021 2.66498 13.0979 2.66498 13.8357 4.00506L21.7984 18.4695C22.4443 19.6428 21.4598 21 19.9627 21H4.0373C2.54022 21 1.55571 19.6428 2.20164 18.4695Z"
                        stroke="#FF3F33"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    ></path>
                    <path
                        d="M12 9V13"
                        stroke="#FF3F33"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    ></path>
                    <path
                        d="M12 17.0195V17"
                        stroke="#FF3F33"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    ></path>
                </g>
            </svg>
        );
    }

    return (
        <svg
            version="1.0"
            id="Layer_1"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 64 64"
            enableBackground="new 0 0 64 64"
            className={`w-6 ${classValue} transition-all duration-300 ease-in-out`}
        >
            <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
            <g
                id="SVGRepo_tracerCarrier"
                strokeLinecap="round"
                strokeLinejoin="round"
            ></g>
            <g id="SVGRepo_iconCarrier">
                <g>
                    <path
                        // fill="#231F20"
                        d="M32,44c6.629,0,12-5.371,12-12V12c0-6.629-5.371-12-12-12S20,5.371,20,12v20C20,38.629,25.371,44,32,44z"
                    ></path>
                    <path
                        // fill="#231F20"
                        d="M52,28c-2.211,0-4,1.789-4,4c0,8.836-7.164,16-16,16s-16-7.164-16-16c0-2.211-1.789-4-4-4s-4,1.789-4,4 c0,11.887,8.656,21.73,20,23.641V60c0,2.211,1.789,4,4,4s4-1.789,4-4v-4.359C47.344,53.73,56,43.887,56,32 C56,29.789,54.211,28,52,28z"
                    ></path>
                </g>
            </g>
        </svg>
    );
}

export default Microphone;
