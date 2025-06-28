// Import necessary libraries
import { Routes, Route } from "react-router-dom";

// pages import
import Layout from "./components/common/layout";
import Homepage from "./components/homepage/homepage";
import Song from "./components/songs/song";
import NotFound from "./components/common/notFound";

// Import CSS styles
import "./App.css";

function App() {
    return (
        <Routes>
            <Route path="/" element={<Layout />}>
                <Route index element={<Homepage />} />
                <Route path="/songs" element={<Song />} />
                <Route path="*" element={<NotFound />} />
            </Route>
        </Routes>
    );
}

export default App;
