import React, { useCallback, useState } from "react";
import useEmblaCarousel from "embla-carousel-react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import Image from "next/image";

interface ImageVariant {
  large?: string;
  thumb?: string;
  hi_res?: string;
  variant?: string;
}

interface ProductCarouselProps {
  images: Record<string, string | ImageVariant>;
}

export const ProductCarousel: React.FC<ProductCarouselProps> = ({ images }) => {
  const [emblaRef, emblaApi] = useEmblaCarousel();
  const [canScrollPrev, setCanScrollPrev] = useState(false);
  const [canScrollNext, setCanScrollNext] = useState(false);

  const onSelect = useCallback(() => {
    if (!emblaApi) return;
    setCanScrollPrev(emblaApi.canScrollPrev());
    setCanScrollNext(emblaApi.canScrollNext());
  }, [emblaApi]);

  React.useEffect(() => {
    if (!emblaApi) return;
    onSelect();
    emblaApi.on('select', onSelect);
    emblaApi.on('reInit', onSelect);
  }, [emblaApi, onSelect]);

  const scrollPrev = () => {
    if (emblaApi) emblaApi.scrollPrev();
  };

  const scrollNext = () => {
    if (emblaApi) emblaApi.scrollNext();
  };

  console.log('ProductCarousel received images:', images);
  
  // Handle both array of URLs and object with image variants
  const imageUrls = Object.values(images).map(img => {
    if (typeof img === 'string') return img;
    if (typeof img === 'object' && img !== null) {
      // Prefer hi_res, then large, then thumb
      return (img as ImageVariant).hi_res || (img as ImageVariant).large || (img as ImageVariant).thumb || '';
    }
    return '';
  }).filter(url => url !== '');

  console.log('Processed image URLs:', imageUrls);

  if (imageUrls.length === 0) {
    return (
      <div className="relative h-72 bg-gray-100 flex items-center justify-center">
        <p className="text-gray-500">No images available</p>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="overflow-hidden" ref={emblaRef}>
        <div className="flex">
          {imageUrls.map((url, index) => {
            console.log(`Rendering image ${index}:`, url);
            return (
              <div
                key={index}
                className="flex-[0_0_100%] min-w-0 relative h-72"
              >
                <Image
                  src={url}
                  alt={`Product image ${index + 1}`}
                  fill
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                  className="object-contain"
                  priority={index === 0}
                  onError={(e) => {
                    console.error('Image failed to load:', url);
                    const target = e.target as HTMLImageElement;
                    target.src = "https://via.placeholder.com/300x200?text=No+Image";
                  }}
                />
              </div>
            );
          })}
        </div>
      </div>
      {imageUrls.length > 1 && (
        <>
          {canScrollPrev && (
            <button
              onClick={scrollPrev}
              className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/80 p-1 rounded-full shadow-md hover:bg-white transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
          )}
          {canScrollNext && (
            <button
              onClick={scrollNext}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/80 p-1 rounded-full shadow-md hover:bg-white transition-colors"
            >
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          )}
        </>
      )}
    </div>
  );
};