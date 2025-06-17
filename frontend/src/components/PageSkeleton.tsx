import { Skeleton } from "@/components/ui/skeleton";

export const PageSkeleton = () => {
  return (
    <div className="flex flex-col h-[calc(100vh+200px)] mx-[10%] my-[5%] w-[80%] bg-gradient-to-b from-white to-gray-50 rounded-2xl shadow-xl">
      <div className="p-8 space-y-6">
        <Skeleton className="h-8 w-1/3 mx-auto" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    </div>
  );
};