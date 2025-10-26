
const Scoreboard = async ({ searchParams }) => {
    const { exercises, scores } = await searchParams;
    const exerciseResults = exercises.split(',').map(exercise => exercise.trim() && exercise > 0);
    const scoreResults = scores.split(',').map(score => score.trim() && score > 0);

    return (
<div>
    <main className="flex min-h-screen w-full flex-col items-center justify-center">

    {/* Background Image */}
    <img src="Background.jpg" className="w-full absolute transform -scale-x-100"/>
    {/* Outside container */}
    <div className="relative bg-linear-to-r from-black from-70% flex flex-4 items-center w-3/5 h-screen mr-auto">

        {/* Inside container */}
        <div className=" w-full pl-30">
        {/* Name */}
        <h1 className="text-6xl text-white">
            <span className="text-8xl font-semibold">Y</span>
            <span className="-m-2.5 font-semibold">OGA</span>
            <span className="text-8xl font-semibold">V</span>
            <span className="font-semibold">ISION</span>
        </h1>

        {/* Slogan */}
        <h3 className="flex text-white text-4xl font-semibold mb-5 ml-5">
            <span className="mr-8">FREE</span>
            <span className="mr-8">FUN</span>
            <span className="mr-8">FIT</span>
        </h3>

        
        {/* Scoreboard */}
        <div>
            <h className="w-[200px] h-full bg-white">Scoreboard</h>
            {exerciseResults.map((line, index) => (
                <div
                key={index}
                className="flex w-full text-black border border-red-500">
                    <h3>{line}</h3>
                    <h3>{scoreResults[index]}</h3>
                </div>
            ))}
        </div>

        {/* Try again */}
        <button className="w-50 px-3 py-3 mb-7 bg-white border-2 rounded-md hover:cursor-pointer hover:bg-blue-500 hover:text-white transition delay-50 ease-in-out">Try Again!</button>
        </div>
    </div>
            
</main>
</div>
    )
}