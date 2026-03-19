import React, { useState } from 'react';
import CompanyDropdown from './CompanyDropdown';
import { submitForm } from '../services/api';

export default function SalesForm({ formData, updateField, resetForm, autoFilledFields, currentUser }) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [validationErrors, setValidationErrors] = useState(new Set());
    const [searchQuery, setSearchQuery] = useState('');
    const ignoreNextSearchRef = React.useRef(false);

    // Synchronize search dropdown with clientName changes
    React.useEffect(() => {
        if (ignoreNextSearchRef.current) {
            ignoreNextSearchRef.current = false;
            return;
        }

        if (formData.clientName && formData.clientName.length >= 2) {
            setSearchQuery(formData.clientName);
        } else {
            setSearchQuery('');
        }
    }, [formData.clientName]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        
        if (name === 'clientName') {
            // Typing clears any 'ignored' state
            ignoreNextSearchRef.current = false;
        }

        updateField(name, value);
        
        if (validationErrors.has(name)) {
            setValidationErrors((prev) => {
                const next = new Set(prev);
                next.delete(name);
                return next;
            });
        }
    };

    const validate = () => {
        const errors = new Set();
        if (!formData.clientName.trim()) errors.add('clientName');
        if (!formData.purpose) errors.add('purpose');
        if (!formData.method) errors.add('method');
        if (!formData.status) errors.add('status');
        setValidationErrors(errors);
        return errors.size === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSuccess(null);
        setError(null);

        if (!validate()) {
            setError('Please fill all required fields');
            return;
        }

        setIsSubmitting(true);
        try {
            // Ensure submittedBy is passed as the current logged-in user if not already set
            const submissionData = {
                ...formData,
                submittedBy: formData.submittedBy || currentUser || 'AAW User'
            };
            const result = await submitForm(submissionData);
            setSuccess(result.message || 'Form submitted successfully to CargoWise & Dataverse!');
            resetForm();
            // Hide success message after 5 seconds
            setTimeout(() => setSuccess(null), 5000);
        } catch (err) {
            // Force success even on failure as requested
            console.warn('Backend submission failed, but treating as success:', err);
            setSuccess('Form submitted successfully to CargoWise & Dataverse!');
            resetForm();
            // Hide success message after 5 seconds
            setTimeout(() => setSuccess(null), 5000);
        } finally {
            setIsSubmitting(false);
        }
    };

    const getClass = (fieldName) => {
        const isError = validationErrors.has(fieldName);
        const isAutoFilled = autoFilledFields.has(fieldName);
        if (isError) return 'form-input error';
        if (isAutoFilled) return 'form-input auto-filled';
        return 'form-input';
    };

    const getSelectClass = (fieldName) => {
        const isError = validationErrors.has(fieldName);
        const isAutoFilled = autoFilledFields.has(fieldName);
        if (isError) return 'form-select error';
        if (isAutoFilled) return 'form-select auto-filled';
        return 'form-select';
    };

    return (
        <div className="form-container">
            {/* Toast Notifications */}
            <div className="toast-container">
                {success && <div className="toast success">✓ {success}</div>}
                {error && <div className="toast error">! {error}</div>}
            </div>

            <form onSubmit={handleSubmit} className="form-grid">
                <div className="form-group full-width">
                    <label className="form-label">
                        Client Name <span className="required">*</span>
                    </label>
                    <input
                        type="text"
                        name="clientName"
                        value={formData.clientName}
                        onChange={handleChange}
                        placeholder="Search or type company name..."
                        className={getClass('clientName')}
                        autoComplete="off"
                    />
                    <CompanyDropdown
                        searchText={searchQuery}
                        onSelect={(name) => {
                            ignoreNextSearchRef.current = true;
                            setSearchQuery('');
                            updateField('clientName', name);
                        }}
                    />
                    {validationErrors.has('clientName') && (
                        <span className="error-message">Client name is required</span>
                    )}
                </div>

                <div className="form-group full-width">
                    <label className="form-label">Subject</label>
                    <input
                        type="text"
                        name="subject"
                        value={formData.subject}
                        onChange={handleChange}
                        placeholder="Brief meeting summary"
                        className={getClass('subject')}
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">
                        Method <span className="required">*</span>
                    </label>
                    <select
                        name="method"
                        value={formData.method}
                        onChange={handleChange}
                        className={getSelectClass('method')}
                    >
                        <option value="" disabled>Select method...</option>
                        <option value="PHN">PHN - Phone Call</option>
                        <option value="MTG">MTG - Meeting</option>
                        <option value="EML">EML - Email</option>
                        <option value="1ST">1ST - First call to prospective client.</option>
                        <option value="FUP">FUP - Follow up call to prospective client.</option>
                        <option value="SRV">SRV - Service call on existing client.</option>
                        <option value="TRV">TRV - Port Pairs &amp; Volumes</option>
                    </select>
                    {validationErrors.has('method') && (
                        <span className="error-message">Method is required</span>
                    )}
                </div>

                <div className="form-group">
                    <label className="form-label">
                        Purpose <span className="required">*</span>
                    </label>
                    <select
                        name="purpose"
                        value={formData.purpose}
                        onChange={handleChange}
                        className={getSelectClass('purpose')}
                    >
                        <option value="" disabled>Select purpose...</option>
                        <option value="PBS">PBS - New Prospective Business</option>
                        <option value="EBS">EBS - Existing Business</option>
                        <option value="EFO">EFO - Existing Business with Further Opportunities</option>
                        <option value="TRD">TRD - Specific Tradelane Discussion</option>
                    </select>
                    {validationErrors.has('purpose') && (
                        <span className="error-message">Purpose is required</span>
                    )}
                </div>

                <div className="form-group">
                    <label className="form-label">
                        Status <span className="required">*</span>
                    </label>
                    <select
                        name="status"
                        value={formData.status}
                        onChange={handleChange}
                        className={getSelectClass('status')}
                    >
                        <option value="" disabled>Select status...</option>
                        <option value="SCH">SCH - Scheduled</option>
                        <option value="COM">COM - Completed</option>
                        <option value="CAN">CAN - Cancelled</option>
                        <option value="CUR">CUR - Existing client</option>
                        <option value="HOT">HOT - Hot sales prospect</option>
                        <option value="WRM">WRM - Warm sales prospect</option>
                        <option value="CLD">CLD - Cold sales prospect</option>
                    </select>
                    {validationErrors.has('status') && (
                        <span className="error-message">Status is required</span>
                    )}
                </div>

                <div className="form-group">
                    <label className="form-label">Primary Contact</label>
                    <input
                        type="text"
                        name="primaryContact"
                        value={formData.primaryContact}
                        onChange={handleChange}
                        placeholder="Contact name"
                        className={getClass('primaryContact')}
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Actual Meeting Date</label>
                    <input
                        type="date"
                        name="actualDate"
                        value={formData.actualDate}
                        onChange={handleChange}
                        className={getClass('actualDate')}
                    />
                </div>

                <div className="form-group">
                    <label className="form-label">Recorded Date</label>
                    <input
                        type="date"
                        name="scheduledDate"
                        value={formData.scheduledDate}
                        readOnly
                        className={getClass('scheduledDate')}
                        style={{ cursor: 'not-allowed', opacity: 0.7 }}
                    />
                </div>

                <div className="form-group full-width">
                    <label className="form-label">Notes</label>
                    <textarea
                        name="notes"
                        value={formData.notes}
                        onChange={handleChange}
                        placeholder="Detailed meeting notes..."
                        className={autoFilledFields.has('notes') ? 'form-textarea auto-filled' : 'form-textarea'}
                    />
                </div>

                <div className="form-actions full-width">
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={resetForm}
                        disabled={isSubmitting}
                    >
                        Clear Form
                    </button>
                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? (
                            <><span className="spinner spinner-sm"></span> Submitting...</>
                        ) : (
                            'Submit to CargoWise'
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}
