import { 
  LayoutDashboard, 
  Map, 
  Sparkles, 
  UploadCloud, 
  FolderOpen, 
  CalendarCheck, 
  CalendarClock,
  Bell, 
  User,
  Settings,
  Pill,
  Stethoscope
} from 'lucide-react';

export interface NavItem {
  path: string;
  name: string;
  subtitle: string;
  icon?: any;
  showInSidebar?: boolean;
  isSecondary?: boolean;
}

export const navigationConfig: NavItem[] = [
  {
    path: '/dashboard',
    name: 'Overview',
    subtitle: 'Overview of your active care journey and next steps.',
    icon: LayoutDashboard,
    showInSidebar: true
  },
  {
    path: '/journey',
    name: 'Care Journey Map',
    subtitle: 'Understand exactly how CarePath AI processed your information.',
    icon: Map,
    showInSidebar: true
  },
  {
    path: '/timeline',
    name: 'Patient Timeline',
    subtitle: 'Chronological timeline of your clinical events, uploads, and check-ins.',
    icon: CalendarClock,
    showInSidebar: true
  },
  {
    path: '/analysis',
    name: 'AI Analysis',
    subtitle: 'Evidence-backed specialist matching and clinical reasoning reports.',
    icon: Sparkles,
    showInSidebar: true
  },
  {
    path: '/analysis/processing',
    name: 'AI Analysis',
    subtitle: 'CarePath multi-agent routing engines are processing your context.',
    showInSidebar: false
  },
  {
    path: '/upload',
    name: 'Upload Center',
    subtitle: 'Submit medical imaging, lab reports, or medication prescriptions.',
    icon: UploadCloud,
    showInSidebar: true
  },
  {
    path: '/records',
    name: 'My Records',
    subtitle: 'Your organized library of extracted clinical documents and scripts.',
    icon: FolderOpen,
    showInSidebar: true
  },
  {
    path: '/medications',
    name: 'Medications',
    subtitle: 'Track active medication courses and log compliance check-ins.',
    icon: Pill,
    showInSidebar: true
  },
  {
    path: '/followup',
    name: 'Follow-up',
    subtitle: 'Record daily symptom status and log recovery check-ins.',
    icon: CalendarCheck,
    showInSidebar: true
  },
  {
    path: '/doctor-bridge',
    name: 'Doctor Bridge',
    subtitle: 'Prepare appointment briefs and sync guidelines with your doctor.',
    icon: Stethoscope,
    showInSidebar: true
  },
  {
    path: '/follow-up',
    name: 'Follow-up',
    subtitle: 'Record daily symptom status and log recovery check-ins.',
    showInSidebar: false
  },
  {
    path: '/notifications',
    name: 'Notifications',
    subtitle: 'Stay informed of agent outputs, completions, and scheduling updates.',
    icon: Bell,
    showInSidebar: true,
    isSecondary: true
  },
  {
    path: '/profile',
    name: 'Profile',
    subtitle: 'Manage your personal details, allergies, and medical history summary.',
    icon: User,
    showInSidebar: false
  },
  {
    path: '/settings',
    name: 'Settings',
    subtitle: 'Manage your CarePath preferences and experience.',
    icon: Settings,
    showInSidebar: true,
    isSecondary: true
  }
];
