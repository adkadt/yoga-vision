import Image from "next/image";

export default function Home() {
  return (
    <div>
      <main className="flex min-h-screen w-full flex-col items-center justify-center">

        {/* Background Image */}
        <img src="Background.jpg" className="w-full absolute transform -scale-x-100" />
        {/* Outside container */}
        <div className="relative bg-linear-to-r from-black from-60% flex flex-4 items-center w-3/5 h-full mr-auto">

          {/* Inside container */}
          <div className=" w-full pl-30">
            {/* Name */}
            <h1 className="text-5xl text-white">
              <span className="text-7xl font-semibold">Y</span>
              <span className="-m-2.5 font-semibold">OGA</span>
              <span className="text-7xl font-semibold">V</span>
              <span className="font-semibold">ISION</span>
            </h1>

            {/* Slogan */}
            <h3 className="flex text-white text-2xl font-semibold">
              <span className="mr-8">FREE</span>
              <span className="mr-8">FUN</span>
              <span className="mr-8">FIT</span>
            </h3>

            {/* Options */}
            
        </div>
      </div>
        
      </main>
    </div>
  );
}
