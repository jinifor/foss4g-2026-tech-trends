import { Button } from "@/components/ui/button";

type TabItem<T extends string> = {
  id: T;
  label: string;
};

export function SectionTabs<T extends string>({
  activeId,
  items,
  onChange,
}: {
  activeId: T;
  items: TabItem<T>[];
  onChange: (id: T) => void;
}) {
  return (
    <div className="mt-4 flex flex-wrap gap-2 rounded-[1.5rem] border border-primary/20 bg-primary/12 px-3 py-3">
      {items.map((item) => (
        <Button
          key={item.id}
          variant={activeId === item.id ? "default" : "secondary"}
          onClick={() => onChange(item.id)}
        >
          {item.label}
        </Button>
      ))}
    </div>
  );
}
