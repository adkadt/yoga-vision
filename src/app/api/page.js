import { redirect } from "next/navigation";

const enableExercise = async ({searchParams}) => {
    const { exercises } = await searchParams;
    const selectedExercises = exercises.split(',').map(exercise => exercise.trim());
    
    const res = await fetch('http://yogavision.abrandt.xyz/api/updateExercises', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ exercises: selectedExercises })
    });

    const data = await res.json();
    console.log(data);

    redirect('../video2');
}

export default enableExercise;