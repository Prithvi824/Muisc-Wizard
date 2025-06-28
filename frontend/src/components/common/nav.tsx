// import necessary libraries
import { Link, useLocation } from "react-router-dom";

function Nav() {
    // Get the current location
    const location = useLocation();

    return (
        <nav className="font-family-jeju text-lg absolute top-5 right-5 left-5 z-10">
            <ul className="flex justify-between">
                <li>
                    <a className="group mr-4 py-1 relative" href="/">
                        Wizard.Io
                        <span className="absolute right-0 bottom-0 h-[2px] w-0 bg-[#86e2b4] transition-all duration-300 group-hover:w-full group-hover:left-0"></span>
                    </a>
                </li>
                <li className="flex justify-end w-1/2">
                    <a
                        className="group mr-4 relative"
                        href="https://prithvi824.github.io/"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Creator
                        <span className="absolute right-0 bottom-0 h-[2px] w-0 bg-[#86e2b4] transition-all duration-300 group-hover:w-full group-hover:left-0"></span>
                    </a>
                    {location.pathname === "/songs" ? (
                        <Link to="/" className="group relative">
                            Recognize
                            <span className="absolute right-0 bottom-0 h-[2px] w-0 bg-[#86e2b4] transition-all duration-300 group-hover:w-full group-hover:left-0"></span>
                        </Link>
                    ) : (
                        <Link to="/songs" className="group relative">
                            Songs
                            <span className="absolute right-0 bottom-0 h-[2px] w-0 bg-[#86e2b4] transition-all duration-300 group-hover:w-full group-hover:left-0"></span>
                        </Link>
                    )}
                </li>
            </ul>
        </nav>
    );
}

export default Nav;
