import About from "@/components/home/About";
import DownloadApp from "@/components/home/DownloadApp";
import Hero from "@/components/home/Hero";
import HowItWorks from "@/components/home/HowItWorks";
import JoinSubscribe from "@/components/home/JoinSubscribe";
import Stories from "@/components/home/Stories";
import Footer from "@/components/navigation/footer";
import Navbar from "@/components/navigation/navbar";

export default function JamRockClimbers() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <Navbar />
      {/* Hero Section */}
      <Hero />

      {/* About Section */}
      <About />

      {/* Function Section */}
      <HowItWorks />

      {/* Download App Section */}
      <DownloadApp />

      {/* Join Section */}
      <JoinSubscribe />

      {/* Footer */}
      <Footer />
    </div>
  );
}
