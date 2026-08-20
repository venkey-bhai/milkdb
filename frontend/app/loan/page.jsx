"use client";

import { useEffect, useState } from "react";
import Sidebar from "../../components/Navbar";

export default function LoanPage() {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [selectedLoan, setSelectedLoan] = useState(null);
  const [customerNo, setCustomerNo] = useState("");

  const [form, setForm] = useState({
    milk_sale_amount: "",
    deduct_amount: "",
  });

  const API =
    process.env.NEXT_PUBLIC_API_URL ||
    "http://127.0.0.1:8000";

  const fetchLoans = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await fetch(
        customerNo
          ? `${API}/loan/${customerNo}`
          : `${API}/loan`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!res.ok) {
        const msg = await res.text();
         console.log(msg);
         throw new Error( `Status ${res.status}`);
      }

      const result = await res.json();

      setLoans(result || []);
    } catch (err) {
      setError("Failed to load loans");
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLoans();
  }, []);

  const deductLoan = async () => {
    if (!selectedLoan) return;

    setLoading(true);
    setError("");

    try {
      const res = await fetch(
        `${API}/${selectedLoan.id}/deduct`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            milk_sale_amount: Number(form.milk_sale_amount),
            deduct_amount: Number(form.deduct_amount),
          }),
        }
      );

      const result = await res.json();

      if (!res.ok) {      
        throw new Error(
          result.detail ||
            "Failed to update loan"
        );
      }

      alert("Loan Updated Successfully");

      setSelectedLoan(null);

      setForm({
        milk_sale_amount: "",
        deduct_amount: "",
      });

      fetchLoans();

    } catch (err) {
      setError(err.message || "Failed to update loan" );
      
      alert(  err.message || "Failed to update loan");
    } finally { setLoading(false);
    }
  };

  const formatCurrency = (amount) =>
    new Intl.NumberFormat(
      "en-IN",
      {
        style: "currency",
        currency: "INR",
      }
    ).format(amount || 0);

  return (
    <div className="flex min-h-screen bg-gray-100">

      <Sidebar />

      <div className="p-10 flex-1">

        <h1 className="text-3xl font-bold mb-5 text-slate-900">
          Loan Management
        </h1>

        <div className="mb-5 flex items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">

           <input
            type="text"
            placeholder="Search customer no..."
            value={customerNo}
            onChange={(e) => setCustomerNo(e.target.value)}
            className="w-full md:w-1/3 rounded-lg border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-slate-400 focus:bg-white"
          /> 

            <button
            onClick={fetchLoans}
            className="rounded-lg border border-black bg-white px-5 py-3 text-sm font-semibold hover:bg-gray-100"
          >
            Search
          </button>    

        </div>

        {error && (
          <div className="bg-red-100 text-red-600 p-3 rounded mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="p-5">
            Loading loans...
          </div>
        ) : (

          <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">

            <table className="w-full border-collapse text-sm">

              <thead>

                <tr className="bg-slate-50">

                  <th className="px-4 py-3 text-xs font-semibold uppercase text-slate-600">
                    Customer
                  </th>

                  <th className="px-4 py-3 text-xs font-semibold uppercase text-slate-600">
                    Loan
                  </th>

                  <th className="px-4 py-3 text-xs font-semibold uppercase text-slate-600">
                    Deducted
                  </th>

                  <th className="px-4 py-3 text-xs font-semibold uppercase text-slate-600">
                    Balance
                  </th>

                  <th className="px-4 py-3 text-xs font-semibold uppercase text-slate-600">
                    Final Payable
                  </th>

                  <th className="px-4 py-3 text-xs font-semibold uppercase text-slate-600">
                    Action
                  </th>

                </tr>

              </thead>

              <tbody>

                {loans.length > 0 ? (

                  loans.map((loan) => (

                    <tr
                      key={loan.id}
                      className="border-t border-slate-100 even:bg-slate-50/60 hover:bg-slate-100/70"
                    >

                      <td className="px-4 py-3">
                        {loan.customer_no}
                      </td>

                      <td className="px-4 py-3 font-medium">
                        {formatCurrency(
                          loan.total_loan
                        )}
                      </td>

                      <td className="px-4 py-3">
                        {formatCurrency(
                          loan.deducted_amount
                        )}
                      </td>

                      <td className="px-4 py-3">
                        {formatCurrency(
                          loan.remaining_balance
                        )}
                      </td>

                      <td className="px-4 py-3">
                        {formatCurrency(
                          loan.final_payable
                        )}
                      </td>

                      <td className="px-4 py-3">

                        <button
                          onClick={() =>
                            setSelectedLoan(
                              loan
                            )
                          }
                          className="rounded-md border border-black bg-white px-3 py-2 text-sm font-semibold hover:bg-gray-100"
                        >
                          Deduct
                        </button>

                      </td>

                    </tr>

                  ))

                ) : (

                  <tr>

                    <td
                      colSpan={6}
                      className="px-5 py-8 text-center text-slate-500"
                    >
                      No Loan Records Found
                    </td>

                  </tr>

                )}

              </tbody>

            </table>

          </div>
        )}
      </div>

      {selectedLoan && (

        <div className="fixed inset-0 bg-black/40 flex items-center justify-center">

          <div className="bg-white w-[420px] rounded-2xl p-6 shadow-lg">

            <h2 className="text-xl font-bold mb-4">
              Deduct Loan
            </h2>

            <input
              type="number"
              placeholder="Milk Sale Amount"
              value={form.milk_sale_amount}
              onChange={(e) =>
                setForm({
                  ...form,
                  milk_sale_amount:
                    e.target.value,
                })
              }
              className="w-full mb-3 rounded-lg border border-slate-300 bg-slate-50 px-4 py-3"
            />

            <input
              type="number"
              placeholder="Deduct Amount"
              value={form.deduct_amount}
              onChange={(e) =>
                setForm({
                  ...form,
                  deduct_amount:
                    e.target.value,
                })
              }
              className="w-full mb-5 rounded-lg border border-slate-300 bg-slate-50 px-4 py-3"
            />

            <div className="flex justify-end gap-3">

              <button
                onClick={() =>
                  setSelectedLoan(null)
                }
                className="rounded-md border border-black bg-white px-4 py-2 hover:bg-gray-100"
              >
                Cancel
              </button>

              <button
                onClick={deductLoan}
                className="rounded-md border border-black bg-white px-4 py-2 hover:bg-gray-100"
              >
                Submit
              </button>

            </div>

          </div>

        </div>

      )}

    </div>
  );
}

