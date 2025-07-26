import React, { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Drawer, DrawerTrigger, DrawerContent, DrawerTitle } from '@/components/ui/drawer';
import SearchResults from './SearchResults';

export function Header() {

  const [term, setTerm] = useState('');
  const [visible, setVisible] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setTerm(value);
    setVisible(value.trim().length > 0);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    if (!e.relatedTarget) {
      setVisible(false);
    }
  };

  return (
    <header className="flex items-center justify-between border-b bg-background p-4">
      <div className="flex items-center gap-2">
        <span className="rounded bg-primary px-2 py-1 text-white">GLPI</span>
        <h1 className="text-lg font-bold">Dashboard</h1>
      </div>
      <div className="flex items-center gap-2">
        <div className="relative">
          <Input
            ref={inputRef}
            placeholder="Buscar..."
            className="pl-8"
            value={term}
            onChange={handleChange}
            onBlur={handleBlur}
            aria-controls="search-results"
            aria-expanded={visible}
          />
          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground">
            <i className="fas fa-search" />
          </span>
          <SearchResults term={term} visible={visible} id="search-results" />
        </div>
        <Button className="btn-outline">Atualizar</Button>
        <Drawer>
          <DrawerTrigger asChild>
            <Button className="btn-outline">
              <i className="fas fa-filter mr-2" />Filtros
            </Button>
          </DrawerTrigger>
          <DrawerContent>
            <DrawerTitle className="text-lg font-bold">Filtros</DrawerTitle>
            {/* Add filter options here */}
          </DrawerContent>
        </Drawer>
      </div>
    </header>
  );
}
