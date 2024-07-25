import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import headerImage from './logo.png';
import './Show.css';

const get_diary = async (uid) => {
    const response = await fetch(`http://172.10.5.46:80/read/${uid}`, {
        method: 'GET'
    });

    const data = await response.json();
    // console.log(data);

    const resp = data.diaries.map(entry => ({
        created_at: entry.created_at,
        type: entry.type,
        content: entry.type === 'chat' ? JSON.stringify(entry.summary.output) : JSON.stringify(entry.content), // Assuming 'entry.emotion' might be an object
        id: entry.id,
        color: entry.color,
        summary: JSON.stringify(entry.summary) // Assuming 'entry.summary' might be an object
    }));

    // Sort the resp array by created_at in descending order
    resp.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    console.log(resp, uid);
    return resp;
}

const Show = () => {
    const location = useLocation();
    const userId = location.state?.userId;
    const navigate = useNavigate();
    const [diaryData, setDiaryData] = useState([]);

    const handleLogoClick = () => {
        navigate('/main', { state: { userId } });
    };

    useEffect(() => {
        const fetchDiary = async () => {
            const tmp = await get_diary(userId);
            setDiaryData(tmp);
        };

        fetchDiary();
    }, [userId]);

    return (
        <div className="MainPage">
            <div className="Main-header">
                <img
                    src={headerImage}
                    alt="Logo"
                    className="header-image"
                    onClick={handleLogoClick}
                    style={{ cursor: 'pointer' }}
                />
            </div>

            <div className="Main-body">
                <div className="grid-container">
                    {diaryData.map((entry, index) => (
                        <div key={index} className="grid-item">
                            <h3>{entry.created_at}</h3>
                            <p>{entry.type}</p>
                            <p>{entry.content}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Show;
