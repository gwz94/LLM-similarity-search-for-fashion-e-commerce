import React from "react";
import { Star } from "lucide-react";

interface RatingStarsProps {
  rating: number;
  numRatings?: number;
  className?: string;
}

export function RatingStars({ rating, numRatings, className = "" }: RatingStarsProps) {
  const maxStars = 5;
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;

  if (!rating) {
    return null;
  }

  return (
    <div className={`flex items-center gap-1 ${className}`}>
      {[...Array(maxStars)].map((_, index) => (
        <Star
          key={index}
          className={`w-4 h-4 ${
            index < fullStars
              ? 'text-yellow-400 fill-yellow-400'
              : index === fullStars && hasHalfStar
              ? 'text-yellow-400 fill-yellow-400/50'
              : 'text-gray-300'
          }`}
        />
      ))}
      <span className="text-sm text-gray-600 ml-1">
        ({rating.toFixed(1)})
        {numRatings !== undefined && (
          <span className="ml-1">• {numRatings} {numRatings === 1 ? 'rating' : 'ratings'}</span>
        )}
      </span>
    </div>
  );
} 