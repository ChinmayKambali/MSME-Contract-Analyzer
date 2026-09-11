import { Link } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
export default function NotFound() { return <MainLayout><div className="grid min-h-[50vh] place-items-center text-center"><div><p className="text-sm font-semibold uppercase tracking-wider text-[#d97745]">404</p><h1 className="mt-2 text-4xl font-bold text-[#163b43]">That page does not exist.</h1><Link to="/" className="mt-6 inline-block font-semibold text-[#287365]">Return to upload</Link></div></div></MainLayout>; }
