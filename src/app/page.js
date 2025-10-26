'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [exerciseList, setExerciseList] = useState([]);
  const [exercisePage, setExercisePage] = useState(0);
  const [chosenExercises, setChosenExercises] = useState([]);
  const [counter, setCounter] = useState(0);
  const [isClicked, setIsClicked] = useState([]);
  const [hovered, setHovered] = useState(false);

  const router = useRouter();

  const filterExercises = async (category) => {
    const response = await fetch('./data/sorted_exercises.json');

    if (response.ok) {
      try {
        const data = await response.json();
        const wantedData = data[category];

        const exerciseNames = wantedData.map(exerciseName => exerciseName.exercise);
        setExerciseList(exerciseNames);
        
      }
      catch (error) {
        console.log("Something wrong while fetching the exercises!");
      }
    }
  }

  const addExercise = (newExercise, index) => {
    if (!chosenExercises.includes(newExercise)) {
      chosenExercises.push(newExercise);
      isClicked.push(index);
      console.log(chosenExercises);
    }
  }

  const getStarted = () => {
    router.push(`/api?exercises=${chosenExercises}`);
  }


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

            {exercisePage === 1 ? (
              <h4 className="text-xl mb-3 ml-5">
                CHOOSE YOUR EXERCISE
                <div className="mt-5 text-black font-bold flex flex-col">
                  {exerciseList.map((line, index) => (
                      <button
                      onClick={() => addExercise(line, index)}
                      onMouseEnter={() => setHovered(true)}
                      onMouseLeave={() => setHovered(false)}  
                      key={index}
                      className={
                        isClicked.includes(index)
                        ? "w-50 px-3 py-3 mb-7 border-2 rounded-md hover:cursor-pointer bg-blue-500 text-white"
                        : "w-50 px-3 py-3 mb-7 bg-white border-2 rounded-md hover:cursor-pointer hover:bg-blue-500 hover:text-white transition delay-50 ease-in-out"
                      }>
                      {line}
                      </button>
                  ))}

                  <button 
                  onClick={() => getStarted()}
                  className='hover:cursor-pointer hover:bg-purple-500 bg-amber-500 rounded-md w-50 p-5 text-white transition delay-50 ease-in-out'>Get Started</button>
                </div>
              </h4>
            )
            : (
              <h4 className="text-xl mb-3 ml-5">
                CHOOSE YOUR CATEGORY
                {/* Options */}
                <div className="mt-5 text-black font-bold flex flex-col">
                  <button 
                  onClick={() => {
                    filterExercises('Yoga');
                    setExercisePage(1); 
                  }}  
                  className="w-50 px-3 py-3 mb-7 bg-white border-2 rounded-md hover:cursor-pointer hover:bg-blue-500 hover:text-white transition delay-50 ease-in-out">YOGA</button>
                  <button 
                  onClick={() => {
                    filterExercises('Pilates');
                    setExercisePage(1);
                  }}
                  className="w-50 px-3 py-3 mb-7 bg-white border-2 rounded-md hover:cursor-pointer hover:bg-blue-500 hover:text-white transition delay-50 ease-in-out">PILATES</button>
                  <button 
                  onClick={() => {
                    filterExercises('Workout');
                    setExercisePage(1);  
                  }}
                  className="w-50 px-3 py-3 mb-7 bg-white border-2 rounded-md hover:cursor-pointer hover:bg-blue-500 hover:text-white transition delay-50 ease-in-out">WORKOUT</button>
                </div>
              </h4> 
            )}

            
        </div>
      </div>
        
      </main>
    </div>
  );
}
