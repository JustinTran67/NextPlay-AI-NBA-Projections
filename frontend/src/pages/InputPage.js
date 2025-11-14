import InputGameData from '../components/InputGameData';
import { useLocation } from 'react-router-dom';

export default function InputPage() {
    const location = useLocation();
    const playerName = location.state?.playerName
    const teamName = location.state?.teamName

    return (
        <div className="flex flex-col items-center mt-20 mb-40">
            <InputGameData playerName={playerName} teamName={teamName}/>
            <div className="w-[500px] p-4 rounded-lg opacity-0 animate-fadeUp [animation-delay:1s]">
                <p className="text-[32px] font-bold mb-4">Pro Tip</p>
                <p className="text-xl">Input the nearest upcoming game for the most accurate prediction!</p>
            </div>
        </div>
    )
}