import { useState, useEffect } from 'react';

export type DeviceClass = 'desktop' | 'tablet' | 'mobile';

export function useDeviceClass(): DeviceClass {
  const [deviceClass, setDeviceClass] = useState<DeviceClass>(() => {
    if (typeof window === 'undefined') return 'desktop';
    const w = window.innerWidth;
    if (w < 768) return 'mobile';
    if (w < 1280) return 'tablet';
    return 'desktop';
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleResize = () => {
      const w = window.innerWidth;
      if (w < 768) setDeviceClass('mobile');
      else if (w < 1280) setDeviceClass('tablet');
      else setDeviceClass('desktop');
    };

    window.addEventListener('resize', handleResize, { passive: true });
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return deviceClass;
}
