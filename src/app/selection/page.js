const Exercises = async ({ searchParams }) => {
    const { category } = await searchParams;
    
    const exercises = [];

    async function filterExercises() {
        try {
            const response = await fetch('./data/sorted_exercises.json');
            if (response.ok) {
                
            }
        }

        catch (error) {
            console.log("Something wrong while fetching the exercises!")
        }
    }

    return(
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
            <h3 className="flex text-white text-4xl font-semibold mb-5">
              <span className="mr-8">FREE</span>
              <span className="mr-8">FUN</span>
              <span className="mr-8">FIT</span>
            </h3>

            <h4 className="text-xl mb-3">
              CHOOSE YOUR EXERCISE
            </h4>

            {/* Options */}
            <div className="text-black font-bold flex flex-col">
              <button 
            //   onClick={() => handleNavigate('Yoga')}  
              className="w-50 px-3 py-3 mb-7 bg-white border-2 rounded-md hover:cursor-pointer hover:bg-blue-500 hover:text-white transition delay-50 ease-in-out">YOGA</button>
              <button 
            //   onClick={() => handleNavigate('Pilates')}
              className="w-50 px-3 py-3 mb-7 bg-white border-2 rounded-md hover:cursor-pointer hover:bg-blue-500 hover:text-white transition delay-50 ease-in-out">PILATES</button>
              <button 
            //   onClick={() => handleNavigate('Workout')}
              className="w-50 px-3 py-3 mb-7 bg-white border-2 rounded-md hover:cursor-pointer hover:bg-blue-500 hover:text-white transition delay-50 ease-in-out">WORKOUT</button>
            </div>
        </div>
      </div>
        
      </main>
    </div>
    )
}


export default Exercises;