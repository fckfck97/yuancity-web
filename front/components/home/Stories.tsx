import Image from "next/image";


export default function Stories() {

  return(
          <section className="py-20 bg-secondary-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div>
            <div className="bg-chart-4 border-4 border-border shadow-brutal-colored-xl p-4 inline-block mb-12 transform -rotate-1">
              <h2 className="text-4xl md:text-5xl font-bold text-main-foreground">STORIES FROM THE CRAG</h2>
            </div>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <div className="relative bg-black border-4 border-border shadow-[24px_24px_0px_0px_var(--color-border)] overflow-hidden">
                <Image
                  src="/first-lead-story.png"
                  alt="First lead story"
                  width={500}
                  height={300}
                  className="w-full h-64 object-cover"
                />
                <div className="absolute inset-0 bg-overlay flex items-end">
                  <div className="bg-chart-2 border-t-4 border-border p-6 w-full">
                    <h3 className="text-2xl font-bold text-main-foreground mb-2">FIRST LEAD AT RED ROCKS</h3>
                    <button className="text-main-foreground font-medium underline">READ MORE →</button>
                  </div>
                </div>
              </div>
            </div>
            <div>
              <div className="relative bg-black border-4 border-border shadow-[24px_24px_0px_0px_var(--color-border)] overflow-hidden">
                <Image
                  src="/trust-story.png"
                  alt="Building trust story"
                  width={500}
                  height={300}
                  className="w-full h-64 object-cover"
                />
                <div className="absolute inset-0 bg-overlay flex items-end">
                  <div className="bg-chart-3 border-t-4 border-border p-6 w-full">
                    <h3 className="text-2xl font-bold text-main-foreground mb-2">BUILDING TRUST ON THE WALL</h3>
                    <button className="text-main-foreground font-medium underline">READ MORE →</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
  )

}